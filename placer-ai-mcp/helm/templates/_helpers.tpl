{{/*
Expand the name of the chart.
*/}}
{{- define "placer-ai-mcp.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "placer-ai-mcp.fullname" -}}
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
{{- define "placer-ai-mcp.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "placer-ai-mcp.labels" -}}
helm.sh/chart: {{ include "placer-ai-mcp.chart" . }}
{{ include "placer-ai-mcp.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "placer-ai-mcp.selectorLabels" -}}
app.kubernetes.io/name: {{ include "placer-ai-mcp.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "placer-ai-mcp.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "placer-ai-mcp.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the secret to use for Placer.ai API credentials
*/}}
{{- define "placer-ai-mcp.secretName" -}}
{{- if .Values.placerAI.existingSecret }}
{{- .Values.placerAI.existingSecret }}
{{- else }}
{{- printf "%s-secret" (include "placer-ai-mcp.fullname" .) }}
{{- end }}
{{- end }}