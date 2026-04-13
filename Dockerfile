FROM python:3.13.13

WORKDIR /app

#   build-essential is needed for Make
#   gcc is needed for compilation of C
#   sse4.2-support for SIMD support
#   psmisc convenience utilities for managing processes (e.g. killall processes by name)
#   tmux for multiplexing between multiple windows within your interactive docker shell
#   valgrind for memory issue debugging
#   strace for stack profiling & debugging
RUN bash -c 'apt-get update && apt-get install -y \
    apt-utils \
    build-essential \
    gcc \
    curl \
#    sse4.2-support \
    psmisc \
    tmux \
    valgrind \
    strace'

# for test generation
RUN bash -c 'pip install scipy pandas'

# install tools like perf
RUN bash -c 'apt-get update && apt-get install -y linux-perf && \
    rm -rf /var/lib/apt/lists/*'

CMD cd src
CMD make clean && make all && /bin/bash && tmux
