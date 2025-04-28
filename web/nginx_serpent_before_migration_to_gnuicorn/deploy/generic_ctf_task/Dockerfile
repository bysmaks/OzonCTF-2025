FROM debian:bookworm-slim

# Install dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends wget gnupg ca-certificates && \
    wget -O - https://openresty.org/package/pubkey.gpg | apt-key add - && \
    echo "deb http://openresty.org/package/debian buster openresty" | tee /etc/apt/sources.list.d/openresty.list && \
    apt-get update && \
    apt-get install -y openresty && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create required directories
RUN mkdir -p /usr/local/openresty/nginx/lua /etc/openresty/conf.d

ENV TZ=Europe/Moscow
# Set environment variables
ENV FLAG="CTF{nginx_default_server_first_alphabetical}"

# Copy Lua files
COPY lua/ /usr/local/openresty/nginx/lua/

# Copy main NGINX config
COPY nginx.conf /usr/local/openresty/nginx/conf/nginx.conf

# Copy server configuration files
COPY conf.d/20-prize.conf /etc/openresty/conf.d/
COPY conf.d/30-visible-snake.conf /etc/openresty/conf.d/
COPY conf.d/90-decoy.conf /etc/openresty/conf.d/
COPY conf.d/hidden-9999-secret.conf /etc/openresty/conf.d/

# Expose port
EXPOSE 80

# Start OpenResty
CMD ["/usr/bin/openresty", "-g", "daemon off;"]
