"""Render deployment scenarios without a Kubernetes cluster or Docker daemon."""

import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]
HELM = os.environ.get("HELM", "helm")
PRODUCTION = ROOT / "examples/values-production.yaml"
DEVELOPMENT = ROOT / "examples/values-development.yaml"
TEST_KEY = "ab" * 32  # Public fixture, never a deployment secret.


def command(args, env=None):
    return subprocess.run([str(arg) for arg in args], cwd=ROOT, env=env,
                          text=True, encoding="utf-8", capture_output=True, check=False)


def render(values=None, overrides=None):
    args = [HELM, "template", "ournezt", "./charts/ournezt"]
    if values:
        args.extend(["-f", values])
    with tempfile.TemporaryDirectory() as directory:
        if overrides:
            path = Path(directory) / "values.yaml"
            path.write_text(yaml.safe_dump(overrides), encoding="utf-8")
            args.extend(["-f", path])
        result = command(args)
    return result


def documents(result):
    if result.returncode:
        raise AssertionError(result.stderr)
    return [doc for doc in yaml.safe_load_all(result.stdout) if doc]


def resource(docs, kind, suffix):
    return next(doc for doc in docs if doc["kind"] == kind and doc["metadata"]["name"].endswith(suffix))


def pod(docs, suffix):
    return resource(docs, "Deployment", suffix)["spec"]["template"]


def container(docs, suffix):
    return pod(docs, suffix)["spec"]["containers"][0]


def environment(docs, suffix):
    return {entry["name"]: entry for entry in container(docs, suffix)["env"]}


class HelmDeploymentTests(unittest.TestCase):
    def test_unconfigured_production_is_rejected(self):
        result = render()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Production Core requires", result.stderr)

    def test_production_tls_secret_and_ca_wiring(self):
        docs = documents(render(PRODUCTION))
        core, web = environment(docs, "-core"), environment(docs, "-web")
        for suffix in ("-core", "-web"):
            self.assertTrue(container(docs, suffix)["image"].endswith(":v2.0.0"))
            self.assertTrue(all(isinstance(e.get("value", ""), str) for e in environment(docs, suffix).values()))
        self.assertEqual(core["GRPC_ALLOW_INSECURE"]["value"], "false")
        self.assertEqual(core["GRPC_TLS_CERT_FILE"]["value"], "/etc/ournezt/core-tls/tls.crt")
        self.assertEqual(core["RUN_MIGRATIONS"]["value"], "true")
        for name, expected in {"CORE_GRPC_USE_TLS": "true", "CORE_ALLOW_INSECURE": "false",
                               "CORE_GRPC_TLS_INSECURE_SKIP_VERIFY": "false",
                               "CORE_GRPC_TLS_CA_FILE": "/etc/ournezt/core-ca/ca.crt",
                               "CORE_GRPC_TLS_SERVER_NAME": "ournezt-ournezt-core"}.items():
            self.assertEqual(web[name]["value"], expected)
        self.assertEqual(web["CSRF_AUTH_KEY"]["valueFrom"]["secretKeyRef"],
                         {"name": "ournezt-web-csrf", "key": "CSRF_AUTH_KEY"})
        volumes = {v["name"]: v for v in pod(docs, "-web")["spec"]["volumes"]}
        self.assertEqual(volumes["core-grpc-ca"]["secret"]["secretName"], "ournezt-core-ca")
        mounts = {v["name"]: v for v in container(docs, "-web")["volumeMounts"]}
        self.assertTrue(mounts["core-grpc-ca"]["readOnly"])
        self.assertNotIn("core-grpc-tls", mounts)  # Never give Web the server private key.
        self.assertFalse(any(d["kind"] == "Secret" and d["metadata"]["name"].endswith("-csrf") for d in docs))

    def test_development_http_needs_no_production_secret(self):
        web = environment(documents(render(DEVELOPMENT)), "-web")
        self.assertNotIn("CSRF_AUTH_KEY", web)
        self.assertEqual(web["CORE_GRPC_USE_TLS"]["value"], "false")
        self.assertEqual(web["SESSION_COOKIE_SECURE"]["value"], "false")

    def test_trusted_plaintext_requires_both_opt_ins_and_csrf(self):
        values = {"core": {"allowInsecure": True}, "web": {
            "coreAllowInsecure": True, "csrf": {"existingSecret": "persistent-csrf"}}}
        docs = documents(render(overrides=values))
        self.assertEqual(environment(docs, "-core")["GRPC_ALLOW_INSECURE"]["value"], "true")
        self.assertEqual(environment(docs, "-web")["CORE_ALLOW_INSECURE"]["value"], "true")
        values["web"].pop("csrf")
        self.assertIn("Production Web requires web.csrf", render(overrides=values).stderr)
        values["web"]["csrf"] = {"existingSecret": "persistent-csrf"}
        values["web"]["coreAllowInsecure"] = False
        self.assertIn("Production Web requires web.coreGrpcTLS", render(overrides=values).stderr)

    def test_invalid_tls_and_csrf_combinations_are_rejected(self):
        cases = [
            ({"web": {"coreGrpcTLS": {"insecureSkipVerify": "true"}}}, "forbidden in production"),
            ({"web": {"csrf": {"existingSecret": "", "authKey": "invalid"}}}, "64 hexadecimal"),
            ({"web": {"csrf": {"authKey": TEST_KEY}}}, "not both"),
            ({"core": {"tls": {"enabled": False}, "allowInsecure": True}}, "TLS settings must match"),
            ({"core": {"enabled": False}}, "web.coreGrpcAddr is required"),
            ({"core": {"allowInsecure": "false"}}, "Invalid type"),
        ]
        for overrides, expected in cases:
            with self.subTest(expected=expected):
                result = render(PRODUCTION, overrides)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(expected, result.stderr)
        result = render(DEVELOPMENT, {"web": {"coreGrpcTLS": {"caSecret": "unused-ca"}}})
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("TLS settings require", result.stderr)

    def test_inline_csrf_key_is_stable_and_rotation_rolls_web(self):
        values = {"web": {"replicaCount": 2, "csrf": {"existingSecret": "", "authKey": TEST_KEY}}}
        first = documents(render(PRODUCTION, values))
        self.assertEqual(first, documents(render(PRODUCTION, values)))
        self.assertEqual(resource(first, "Secret", "-csrf")["stringData"]["CSRF_AUTH_KEY"], TEST_KEY)
        self.assertEqual(resource(first, "Deployment", "-web")["spec"]["replicas"], 2)
        checksum = pod(first, "-web")["metadata"]["annotations"]["checksum/csrf"]
        values["web"]["csrf"]["authKey"] = "cd" * 32
        rotated = documents(render(PRODUCTION, values))
        self.assertNotEqual(checksum, pod(rotated, "-web")["metadata"]["annotations"]["checksum/csrf"])

    def test_system_ca_external_core_and_disabled_web_modes(self):
        docs = documents(render(PRODUCTION, {"web": {"coreGrpcTLS": {"caSecret": ""}}}))
        self.assertNotIn("CORE_GRPC_TLS_CA_FILE", environment(docs, "-web"))
        docs = documents(render(PRODUCTION, {"core": {"enabled": False},
                                            "web": {"coreGrpcAddr": "proxy.example.com:443"}}))
        self.assertEqual(environment(docs, "-web")["CORE_GRPC_ADDR"]["value"], "proxy.example.com:443")
        self.assertFalse(any(d["kind"] == "Deployment" and d["metadata"]["name"].endswith("-core") for d in docs))
        docs = documents(render(overrides={"web": {"enabled": False}, "core": {"allowInsecure": True}}))
        self.assertFalse(any(d["kind"] == "Deployment" and d["metadata"]["name"].endswith("-web") for d in docs))

    def test_custom_secret_keys_and_http_limits(self):
        docs = documents(render(PRODUCTION, {"web": {
            "csrf": {"key": "signing-key"}, "requestTimeout": "7s", "shutdownTimeout": "12s",
            "httpLimits": {"readHeaderTimeout": "11s", "readTimeout": "16s", "writeTimeout": "31s",
                           "idleTimeout": "61s", "maxRequestBodyBytes": 2097152},
            "coreGrpcTLS": {"caKey": "root.pem", "caFileName": "root.pem", "caMountPath": "/trust"}}}))
        web = environment(docs, "-web")
        self.assertEqual(web["CSRF_AUTH_KEY"]["valueFrom"]["secretKeyRef"]["key"], "signing-key")
        self.assertEqual(web["CORE_GRPC_TLS_CA_FILE"]["value"], "/trust/root.pem")
        expected = {"REQUEST_TIMEOUT": "7s", "SHUTDOWN_TIMEOUT": "12s", "WEB_READ_HEADER_TIMEOUT": "11s",
                    "WEB_READ_TIMEOUT": "16s", "WEB_WRITE_TIMEOUT": "31s", "WEB_IDLE_TIMEOUT": "61s",
                    "WEB_MAX_REQUEST_BODY_BYTES": "2097152"}
        for key, value in expected.items():
            self.assertEqual(web[key]["value"], value)


class ComposeDeploymentTests(unittest.TestCase):
    def compose(self, *files, overrides=None):
        env = os.environ.copy()
        for line in (ROOT / ".env.example").read_text(encoding="utf-8").splitlines():
            if line and not line.startswith("#") and "=" in line:
                env.pop(line.split("=", 1)[0], None)
        env.update(overrides or {})
        args = ["docker", "compose", "--env-file", ".env.example", "-f", "docker-compose.yml"]
        for path in files:
            args.extend(["-f", path])
        result = command(args + ["config", "--format", "json"], env)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)["services"]

    def test_released_defaults_and_local_builds(self):
        services = self.compose()
        self.assertEqual(services["core"]["image"], "ghcr.io/ournezt/ournezt-core:v2.0.0")
        self.assertEqual(services["web"]["image"], "ghcr.io/ournezt/ournezt-web:v2.0.0")
        self.assertEqual(services["web"]["environment"]["WEB_MAX_REQUEST_BODY_BYTES"], "1048576")
        services = self.compose("docker-compose.build.yml")
        self.assertEqual(services["core"]["image"], "ournezt-core:local")
        self.assertEqual(services["web"]["image"], "ournezt-web:local")

    def test_production_environment_interpolation(self):
        services = self.compose(overrides={
            "CORE_APP_ENV": "production", "WEB_APP_ENV": "production", "WEB_CSRF_AUTH_KEY": TEST_KEY,
            "CORE_GRPC_ALLOW_INSECURE": "true", "WEB_CORE_ALLOW_INSECURE": "true",
            "WEB_SESSION_COOKIE_SECURE": "true", "WEB_READ_TIMEOUT": "20s"})
        self.assertEqual(services["core"]["environment"]["GRPC_ALLOW_INSECURE"], "true")
        web = services["web"]["environment"]
        for key, expected in {"APP_ENV": "production", "CSRF_AUTH_KEY": TEST_KEY,
                              "CORE_ALLOW_INSECURE": "true", "SESSION_COOKIE_SECURE": "true",
                              "WEB_READ_TIMEOUT": "20s"}.items():
            self.assertEqual(web[key], expected)

    def test_tls_override_mounts_only_required_credentials(self):
        services = self.compose("docker-compose.tls.yml")
        self.assertEqual(services["core"]["environment"]["GRPC_TLS_KEY_FILE"], "/etc/ournezt/core-tls/tls.key")
        web = services["web"]["environment"]
        for key, expected in {"CORE_GRPC_USE_TLS": "true", "CORE_GRPC_TLS_SERVER_NAME": "core",
                              "CORE_ALLOW_INSECURE": "false", "CORE_GRPC_TLS_INSECURE_SKIP_VERIFY": "false"}.items():
            self.assertEqual(web[key], expected)
        self.assertEqual(len(services["web"]["volumes"]), 1)
        for name in ("core", "web"):
            volume = services[name]["volumes"][0]
            self.assertTrue(volume["read_only"])
            self.assertFalse(volume["bind"].get("create_host_path", False))
        combined = self.compose("docker-compose.build.yml", "docker-compose.tls.yml")
        self.assertEqual(combined["web"]["image"], "ournezt-web:local")
        self.assertEqual(combined["web"]["environment"]["CORE_GRPC_USE_TLS"], "true")


if __name__ == "__main__":
    unittest.main()
