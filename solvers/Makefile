CC := gcc
CXX := g++
CFLAGS := -O3 -std=c11 -Wall -Wextra -Werror
CXXFLAGS := -O3 -std=c++17 -Wall -Wextra -Werror

C_SOURCES := $(filter-out %.lean.c, $(wildcard *.c))
CPP_SOURCES := $(wildcard *.cpp)

C_OUTPUTS := $(C_SOURCES:.c=_c.out)
CPP_OUTPUTS := $(CPP_SOURCES:.cpp=_cpp.out)

.PHONY: all c cpp clean

all: $(C_OUTPUTS) $(CPP_OUTPUTS)
c: $(C_OUTPUTS)
cpp: $(CPP_OUTPUTS)

%_c.out: %.c
	$(CC) $(CFLAGS) -o $@ $<

%_cpp.out: %.cpp
	$(CXX) $(CXXFLAGS) -o $@ $<

clean:
	rm -f $(C_OUTPUTS) $(CPP_OUTPUTS) *.lean.c
