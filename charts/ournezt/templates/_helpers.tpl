{{- define "ournezt.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "ournezt.fullname" -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- printf "%s-%s" .Release.Name (include "ournezt.name" .) | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}

{{- define "ournezt.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" -}}
{{- end -}}

{{- define "ournezt.labels" -}}
helm.sh/chart: {{ include "ournezt.chart" . }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

{{- define "ournezt.postgres.fullname" -}}
{{- printf "%s-postgres" (include "ournezt.fullname" .) | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "ournezt.core.fullname" -}}
{{- printf "%s-core" (include "ournezt.fullname" .) | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "ournezt.web.fullname" -}}
{{- printf "%s-web" (include "ournezt.fullname" .) | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "ournezt.postgres.selectorLabels" -}}
app.kubernetes.io/name: {{ include "ournezt.name" . }}-postgres
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

{{- define "ournezt.core.selectorLabels" -}}
app.kubernetes.io/name: {{ include "ournezt.name" . }}-core
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

{{- define "ournezt.web.selectorLabels" -}}
app.kubernetes.io/name: {{ include "ournezt.name" . }}-web
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}
