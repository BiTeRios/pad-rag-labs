# UI: статика + nginx (прокси /api на gateway). Сборка: docker build -t rag/web:1.0.0 lab2/ui
# nginx-unprivileged: процесс не root (uid 101), порт 8080; сборка фронтенда не нужна — файлы отдаются как есть.
FROM nginxinc/nginx-unprivileged:1.29-alpine

# Адрес gateway подставляется в шаблон при старте (envsubst образа nginx); в Kubernetes — из ConfigMap.
# Число worker-процессов nginx — по лимиту CPU контейнера, а не по числу ядер узла.
ENV GATEWAY_URL=http://gateway:8000 \
    NGINX_ENTRYPOINT_WORKER_PROCESSES_AUTOTUNE=1

COPY nginx/default.conf.template /etc/nginx/templates/default.conf.template
COPY static/ /usr/share/nginx/html/

EXPOSE 8080
HEALTHCHECK --interval=15s --timeout=3s CMD wget -qO /dev/null http://127.0.0.1:8080/healthz || exit 1
