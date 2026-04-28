all: main test benchmark

# C-compiler settings
CC = gcc -std=c99 -g -ggdb3

# Default optimization level
O ?= 0

# Flags and other libraries
override CFLAGS += -Wall -Wextra -pedantic -O$(O)
LDFLAGS =
LIBS =

# Root build output directories (relative to src/hash_table)
BUILD_DIR ?= ../../build
BINDIR := $(BUILD_DIR)/bin/hash_table
OBJDIR := $(BUILD_DIR)/obj/hash_table
DEPSDIR := $(BUILD_DIR)/dep/hash_table

MAIN_BIN := $(BINDIR)/main
TEST_BIN := $(BINDIR)/test
BENCHMARK_BIN := $(BINDIR)/benchmark

# objects needed for dependencies
OBJECTS := hash_table.o list_node.o value_array.o
OBJFILES := $(addprefix $(OBJDIR)/,$(OBJECTS))

####### Automatic dependency magic #######
BUILDSTAMP := $(DEPSDIR)/rebuildstamp
DEPFILES := $(wildcard $(DEPSDIR)/*.d)
ifneq ($(DEPFILES),)
include $(DEPFILES)
endif
DEPCFLAGS = -MD -MF $(DEPSDIR)/$*.d -MP

ifneq ($(DEP_CC),$(CC) $(CFLAGS) $(DEPCFLAGS) $(O))
DEP_CC := $(shell mkdir -p $(DEPSDIR); echo >$(BUILDSTAMP); echo "DEP_CC:=$(CC) $(CFLAGS) $(DEPCFLAGS) $(O)" >$(DEPSDIR)/_cc.d)
endif

$(DEPSDIR)/stamp $(BUILDSTAMP):
	mkdir -p $(@D)
	touch $@
####### Automatic dependency magic #######

$(OBJDIR)/%.o : %.c $(BUILDSTAMP)
	mkdir -p $(@D)
	$(CC) $(CFLAGS) $(DEPCFLAGS) -O$(O) -o $@ -c $<

main: $(MAIN_BIN)
$(MAIN_BIN): $(OBJFILES) $(OBJDIR)/main.o
	mkdir -p $(@D)
	$(CC) $(CFLAGS) $(DEPCFLAGS) -o $@ $^ $(LDFLAGS) $(LIBS)

test: $(TEST_BIN)
$(TEST_BIN): $(OBJFILES) $(OBJDIR)/test.o
	mkdir -p $(@D)
	$(CC) $(CFLAGS) $(DEPCFLAGS) -o $@ $^ $(LDFLAGS) $(LIBS)

benchmark: $(BENCHMARK_BIN)
$(BENCHMARK_BIN): $(OBJFILES) $(OBJDIR)/benchmark.o
	mkdir -p $(@D)
	$(CC) $(CFLAGS) $(DEPCFLAGS) -o $@ $^ $(LDFLAGS) $(LIBS)

clean:
	rm -rf $(BUILD_DIR) *~ *.bak core *.core

.PHONY: all main test benchmark clean
