{{- define "ournezt-postgres.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "ournezt-postgres.fullname" -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- printf "%s-%s" .Release.Name (include "ournezt-postgres.name" .) | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}

{{- define "ournezt-postgres.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" -}}
{{- end -}}

{{- define "ournezt-postgres.labels" -}}
helm.sh/chart: {{ include "ournezt-postgres.chart" . }}
app.kubernetes.io/name: {{ include "ournezt-postgres.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}

{{- define "ournezt-postgres.selectorLabels" -}}
app.kubernetes.io/name: {{ include "ournezt-postgres.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}
