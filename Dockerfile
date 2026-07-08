FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV ANDROID_HOME=/opt/android-sdk
ENV ANDROID_SDK_ROOT=/opt/android-sdk
ENV ANDROID_COMMANDLINE_TOOLS_ZIP=commandlinetools-linux-14742923_latest.zip
ENV ANDROID_BUILD_TOOLS_VERSION=36.0.0
ENV ANDROID_LEGACY_PLATFORM_VERSION=29
ENV ANDROID_LEGACY_BUILD_TOOLS_VERSION=29.0.3
ENV GRADLE_VERSION=9.5.0
ENV GRADLE_HOME=/opt/gradle
ENV GRADLE_COMPAT_VERSIONS="8.13 8.14.3 6.1.1 5.1.1 4.6"
ENV JAVA11_HOME=/opt/jdk-11
ENV PATH="${GRADLE_HOME}/bin:${ANDROID_HOME}/cmdline-tools/latest/bin:${ANDROID_HOME}/platform-tools:${ANDROID_HOME}/build-tools/${ANDROID_BUILD_TOOLS_VERSION}:${PATH}"

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        default-jdk-headless \
        git \
        npm \
        unzip \
    && rm -rf /var/lib/apt/lists/*

RUN curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b /usr/local/bin \
    && curl -sSfL https://raw.githubusercontent.com/anchore/grype/main/install.sh | sh -s -- -b /usr/local/bin \
    && curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin \
    && curl -fsSL https://github.com/CycloneDX/cyclonedx-cli/releases/latest/download/cyclonedx-linux-x64 -o /usr/local/bin/cyclonedx \
    && chmod +x /usr/local/bin/cyclonedx \
    && ln -sf /usr/local/bin/cyclonedx /usr/local/bin/cyclonedx-cli \
    && npm install -g @cyclonedx/cdxgen

RUN curl -fsSL "https://dl.google.com/android/repository/${ANDROID_COMMANDLINE_TOOLS_ZIP}" -o /tmp/android-commandline-tools.zip \
    && mkdir -p "${ANDROID_HOME}/cmdline-tools" \
    && unzip -q /tmp/android-commandline-tools.zip -d /tmp/android-sdk-tools \
    && mv /tmp/android-sdk-tools/cmdline-tools "${ANDROID_HOME}/cmdline-tools/latest" \
    && yes | sdkmanager --sdk_root="${ANDROID_HOME}" --licenses >/dev/null \
    && yes | sdkmanager --sdk_root="${ANDROID_HOME}" \
        "platform-tools" \
        "build-tools;${ANDROID_BUILD_TOOLS_VERSION}" \
        "platforms;android-${ANDROID_LEGACY_PLATFORM_VERSION}" \
        "build-tools;${ANDROID_LEGACY_BUILD_TOOLS_VERSION}" \
    && rm -rf /tmp/android-commandline-tools.zip /tmp/android-sdk-tools

RUN curl -fsSL "https://api.adoptium.net/v3/binary/latest/11/ga/linux/x64/jdk/hotspot/normal/eclipse?project=jdk" -o /tmp/jdk11.tar.gz \
    && mkdir -p "${JAVA11_HOME}" \
    && tar -xzf /tmp/jdk11.tar.gz -C "${JAVA11_HOME}" --strip-components=1 \
    && rm -f /tmp/jdk11.tar.gz

RUN curl -fsSL "https://services.gradle.org/distributions/gradle-${GRADLE_VERSION}-bin.zip" -o /tmp/gradle.zip \
    && unzip -q /tmp/gradle.zip -d /opt \
    && mv "/opt/gradle-${GRADLE_VERSION}" "${GRADLE_HOME}" \
    && rm -f /tmp/gradle.zip

RUN set -eux; \
    for version in ${GRADLE_COMPAT_VERSIONS}; do \
        curl -fsSL "https://services.gradle.org/distributions/gradle-${version}-bin.zip" -o "/tmp/gradle-${version}.zip"; \
        unzip -q "/tmp/gradle-${version}.zip" -d /opt; \
        rm -f "/tmp/gradle-${version}.zip"; \
    done

COPY requirements.txt .
RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app:/app/src

CMD ["python", "scripts/check_toolchain.py"]
