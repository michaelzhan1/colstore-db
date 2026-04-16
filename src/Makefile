all: client server

# C-compiler settings
CC = gcc -std=c99 -g -ggdb3

# Default optimization level
O ?= 0

# Flags and other libraries
override CFLAGS += -Wall -Wextra -pedantic -pthread -O$(O) -I$(INCLUDES)
LDFLAGS =
LIBS =
INCLUDES = include

# this is the DB server and client's unix socket path
SOCK_PATH=\"/tmp/db_unix_socket\"

# Build output directories (root-level build/)
BUILD_DIR ?= ../build
BINDIR := $(BUILD_DIR)/bin
OBJDIR := $(BUILD_DIR)/obj
DEPSDIR := $(BUILD_DIR)/dep

CLIENT_BIN := $(BINDIR)/client
SERVER_BIN := $(BINDIR)/server

OBJECTS := client.o server.o parse.o utils.o db_manager.o client_context.o
OBJFILES := $(addprefix $(OBJDIR)/,$(OBJECTS))

# Set-up dependency directory
BUILDSTAMP := $(DEPSDIR)/rebuildstamp
DEPFILES := $(wildcard $(DEPSDIR)/*.d)
ifneq ($(DEPFILES),)
include $(DEPFILES)
endif
DEPCFLAGS = -MD -MF $(DEPSDIR)/$*.d -MP -DSOCK_PATH=$(SOCK_PATH)

# Dependency compilation
ifneq ($(DEP_CC),$(CC) $(CFLAGS) $(DEPCFLAGS) $(O))
DEP_CC := $(shell mkdir -p $(DEPSDIR); echo >$(BUILDSTAMP); echo "DEP_CC:=$(CC) $(CFLAGS) $(DEPCFLAGS) $(O)" >$(DEPSDIR)/_cc.d)
endif

# Make sure dependency directories are generated
$(DEPSDIR)/stamp $(BUILDSTAMP):
	mkdir -p $(@D)
	touch $@

# force rebuild by buildstamp
$(OBJDIR)/%.o : %.c $(BUILDSTAMP)
	mkdir -p $(@D)
	$(CC) $(CFLAGS) $(DEPCFLAGS) -O$(O) -o $@ -c $<

# build client
client: $(CLIENT_BIN)
$(CLIENT_BIN): $(OBJDIR)/client.o $(OBJDIR)/utils.o
	mkdir -p $(@D)
	$(CC) $(CFLAGS) $(DEPCFLAGS) -o $@ $^ $(LDFLAGS) $(LIBS)

# build server
server: $(SERVER_BIN)
$(SERVER_BIN): $(OBJDIR)/server.o $(OBJDIR)/parse.o $(OBJDIR)/utils.o $(OBJDIR)/db_manager.o $(OBJDIR)/client_context.o
	mkdir -p $(@D)
	$(CC) $(CFLAGS) $(DEPCFLAGS) -o $@ $^ $(LDFLAGS) $(LIBS)

clean:
	rm -rf $(BUILD_DIR) *~ *.bak core *.core $(SOCK_PATH)

.PHONY: all client server clean
