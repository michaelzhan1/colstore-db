FROM ubuntu:24.04

WORKDIR /app

#   build-essential is needed for Make
#   gcc is needed for compilation of C
#   sse4.2-support for SIMD support
#   psmisc convenience utilities for managing processes (e.g. killall processes by name)
#   tmux for multiplexing between multiple windows within your interactive docker shell
#   valgrind for memory issue debugging
#   strace for stack profiling & debugging
RUN bash -c 'apt-get update && apt-get install -y \
    build-essential \
    gcc \
    curl \
#    sse4.2-support \
    psmisc \
    tmux \
    valgrind \
    strace'

# copy perf
RUN bash -c 'apt-get install -y linux-tools-common linux-tools-generic && \
    cd /usr/lib/linux-tools && \
    cd `ls -1 | head -n1` && \
    rm -f /usr/bin/perf && \
    ln -s `pwd`/perf /usr/bin/perf'

RUN bash -c 'rm -rf /var/lib/apt/lists/*'

CMD ["sleep", "infinity"]
