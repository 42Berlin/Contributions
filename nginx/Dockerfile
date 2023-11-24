FROM nginx

COPY nginx.conf /etc/nginx/nginx.conf

RUN mkdir -p /etc/nginx/ssl
COPY ssl/* /etc/nginx/ssl

ENTRYPOINT ["nginx", "-g", "daemon off;"]