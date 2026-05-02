FROM alpine:3.19

# Install runtimes
RUN apk add --no-cache \
    python3 py3-pip \
    openjdk17-jdk \
    g++ \
    musl-dev \
    linux-headers \
    bash \
    coreutils

# Create sandbox user
RUN adduser -D -s /bin/sh sandbox

# Create working directory
WORKDIR /sandbox
RUN chown sandbox:sandbox /sandbox

# Copy executor scripts
COPY --chown=sandbox:sandbox executors/ /executors/

USER sandbox

# Default command
CMD ["sh"]
