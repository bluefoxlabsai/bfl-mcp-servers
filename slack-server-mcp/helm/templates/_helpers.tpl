{{/*
Expand the name of the chart.
*/}}
{{- define "slack-mcp-server.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "slack-mcp-server.fullname" -}}
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
{{- define "slack-mcp-server.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "slack-mcp-server.labels" -}}
helm.sh/chart: {{ include "slack-mcp-server.chart" . }}
{{ include "slack-mcp-server.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "slack-mcp-server.selectorLabels" -}}
app.kubernetes.io/name: {{ include "slack-mcp-server.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "slack-mcp-server.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "slack-mcp-server.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Return true if service should be enabled
*/}}
{{- define "slack-mcp-server.serviceEnabled" -}}
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
{{- define "slack-mcp-server.probesEnabled" -}}
{{- if or (eq .Values.mcp.transport "http") (eq .Values.mcp.transport "sse") }}
{{- print "true" }}
{{- else }}
{{- print "false" }}
{{- end }}
{{- end }}