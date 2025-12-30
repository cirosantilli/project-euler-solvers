CC := gcc
CXX := g++
LEAN := lean
LEANC := leanc
CFLAGS := -O2 -std=c11 -Wall -Wextra -Werror
CXXFLAGS := -O2 -std=c++17 -Wall -Wextra -Werror

C_SOURCES := $(wildcard *.c)
CPP_SOURCES := $(wildcard *.cpp)
LEAN_SOURCES := $(wildcard *.lean)

C_OUTPUTS := $(C_SOURCES:.c=_c.out)
CPP_OUTPUTS := $(CPP_SOURCES:.cpp=_cpp.out)
LEAN_OUTPUTS := $(LEAN_SOURCES:.lean=_lean.out)

.PHONY: all c cpp lean clean

all: $(C_OUTPUTS) $(CPP_OUTPUTS) $(LEAN_OUTPUTS)
c: $(C_OUTPUTS)
cpp: $(CPP_OUTPUTS)
lean: $(LEAN_OUTPUTS)

%_c.out: %.c
	$(CC) $(CFLAGS) -o $@ $<

%_cpp.out: %.cpp
	$(CXX) $(CXXFLAGS) -o $@ $<

%_lean.out: %.lean
	$(LEAN) -c $*.lean.c $<
	$(LEANC) -o $@ $*.lean.c

clean:
	rm -f $(C_OUTPUTS) $(CPP_OUTPUTS) $(LEAN_OUTPUTS) *_lean.c
