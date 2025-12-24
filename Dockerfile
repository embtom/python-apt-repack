FROM debian:trixie AS build-env

ARG DEBIAN_FRONTEND=noninteractive

ENV PIP_ROOT_USER_ACTION=ignore
ENV PIP_BREAK_SYSTEM_PACKAGES=1
ENV LANG=en_US.UTF-8
ENV LC_ALL=en_US.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        ccache \
        cdbs \
        cmake \
        devscripts \
        dirmngr \
        distro-info-data \
        dumb-init \
        equivs \
        git \
        gnupg \
        libapt-pkg-dev \
        libpython3-dev \
        locales \
        ninja-build \
        pkg-config \
        pkgconf \
        pre-commit \
        pybuild-plugin-pyproject \
        pycodestyle \
        pyflakes3 \
        python3-all \
        python3-all-dev \
        python3-build \
        python3-debian \
        python3-dev \
        python3-feedparser \
        python3-pip \
        python3-scikit-build-core \
        python3-sphinx \
        python3-xmlrunner \
        rsync \
        ssh \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && sed -i 's/^# *en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen \
    && locale-gen
   
FROM build-env AS dev-env

RUN apt-get update && apt-get install --yes --no-install-recommends \
        curl \
        default-jdk-headless \
        gdb \
        nano \
        zsh \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && ZSH="/root/.oh-my-zsh" RUNZSH=no CHSH=no \
    sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended

RUN python3 -m pip install --no-cache-dir --break-system-packages \
        cmake-format \
        flake8 \
        mypy

CMD [ "/usr/bin/zsh" ]    
