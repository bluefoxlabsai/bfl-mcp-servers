{{/*
Expand the name of the chart.
*/}}
{{- define "accuweather-mcp.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "accuweather-mcp.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "accuweather-mcp.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "accuweather-mcp.labels" -}}
helm.sh/chart: {{ include "accuweather-mcp.chart" . }}
{{ include "accuweather-mcp.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "accuweather-mcp.selectorLabels" -}}
app.kubernetes.io/name: {{ include "accuweather-mcp.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "accuweather-mcp.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "accuweather-mcp.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Return true if service should be enabled
*/}}
{{- define "accuweather-mcp.serviceEnabled" -}}
{{- $serviceEnabled := .Values.service.enabled | toString -}}
{{- if eq $serviceEnabled "auto" }}
{{- if or (eq .Values.mcp.transport "http") (eq .Values.mcp.transport "sse") }}
{{- print "true" }}
{{- else }}
{{- print "false" }}
{{- end }}
{{- else }}
{{- print $serviceEnabled }}
{{- end }}
{{- end }}

{{/*
Return true if probes should be enabled (for HTTP and SSE transports)
*/}}
{{- define "accuweather-mcp.probesEnabled" -}}
{{- if or (eq .Values.mcp.transport "http") (eq .Values.mcp.transport "sse") }}
{{- print "true" }}
{{- else }}
{{- print "false" }}
{{- end }}
{{- end }}