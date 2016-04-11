# compilation

TARGET = snapshot
SRC = pq.cpp
OBJ = pq.o
CC = g++
DEP = pq.h barrier.h

CFLAGS = -std=c++11 
#CFLAGS += -DDEBUG
INCLUDES = -I/opt/local/include

# link options
LIB_INCLUDES = -L/opt/local/lib
LIBS = -lpthread -lboost_thread-mt -lboost_program_options-mt

ALL: $(TARGET)

$(TARGET): $(OBJ)
	$(CC) $(LFLAGS) -o $@ $^ $(LIB_INCLUDES) $(LIBS)

%.o: %.cpp $(DEP) 
	$(CC) $(CFLAGS) $(INCLUDES) -c -o $@ $<

clean:
	rm $(TARGET) *.o 
