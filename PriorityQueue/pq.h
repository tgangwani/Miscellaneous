// implements the priority queue
#include<atomic>
#include<assert.h>

//#define DEBUG 
#define ONE static_cast<uintptr_t>(1) 
#define ONE_MSB ONE<<63 
#define RC(val) reinterpret_cast<uintptr_t>(val) 

// macro to assert if the last bit of a pointer is 0
#define CHECK_MSB(val) assert((RC(val) & ONE_MSB) == 0);

// node type of the priority queue
template <typename T>
class node {
  public:  
    T data;  // priority
    node<T> *next;  // next pointer (the msb is used to mark logical deletions)

    // constructors
    node(T& _data): data(_data), next(NULL) {}
    node(): next(NULL) {} 
};

template <typename T>
class pq {
  private:
    std::atomic<node<T>*> head;  // (atomic) pointer to the top of the queue 
    node<T> *sentinel;  // node that marks the end of the priority queue

  public:
    pq() {
       sentinel = new node<T>();

       #ifdef DEBUG
         std::cout<<"Sentinel node created at address "<<sentinel<<"\n";
       #endif 

       // assert that the msb is zero. We'll use this for logical deletion
       CHECK_MSB(sentinel); 
       head = sentinel;
    }
  
    ~pq() {
      delete sentinel;
    }

    // function to add to the priority queue
    void enqueue(T& data) {

      // create new node
      node<T> *new_node = new node<T>(data);
      
      #ifdef DEBUG
        std::cout<<"New data node created at address "<<new_node<< " with data " << data<<"\n";
      #endif
      
      // assert that the msb is zero. We'll use this for logical deletion
      CHECK_MSB(new_node);
      auto prev = &head;
      node<T> *curr, *next;
      int d; // takes value from the set {0,1}; 1 = logically deleted node
  
      start:
        curr = head.load(std::memory_order_relaxed);    // load the head

      while(true){
        if(curr == sentinel) break;  // we have reached the end of the priority queue 

        // get the <next, d> pair from curr->next
        d = (RC(curr->next) & ONE_MSB) > 0 ? 1 : 0;  // check if the msb (logical deletion bit) is set
        next = reinterpret_cast<node<T> *> ((RC(curr->next) << ONE) >> ONE);  // remove the msb to fetch next pointer from curr->next
        
        if(d) {

          #ifdef DEBUG
            std::cout<<"Logical bit set\n";
          #endif
            
          // if the logical bit is set, try to physically remove this node from
          // the priority queue using CAS
          node<T> *expected = reinterpret_cast<node<T> *> ((RC(curr) << ONE) >> ONE);
          if(!atomic_compare_exchange_weak_explicit(prev, &expected, next, std::memory_order_release, std::memory_order_relaxed)) {
            goto start;
          }

        }
        // the else condition checks for the correct placement of the node based
        // on the priority
        else {
          if(curr->data >= new_node->data) {
            // go out of the while loop if the position is found
            break; 
          }
          prev = reinterpret_cast<std::atomic<node<T>*>*> (&curr->next);
        }

        #ifdef DEBUG
          std::cout<<"Priority Queue spot rejected. Trying next.\n";
        #endif

        curr = next;
      }

      new_node->next = curr;
      
      // found correct position. Now use CAS to insert the node
      node<T> *expected = reinterpret_cast<node<T> *> ((RC(curr) << ONE) >> ONE);
      // insert node between prev and curr
      if(!atomic_compare_exchange_weak_explicit(prev, &expected, new_node, std::memory_order_release, std::memory_order_relaxed)) {
        goto start;
      }

      #ifdef DEBUG
        std::cout<<"Node inserted successfully!\n";
      #endif
    }

    void dequeue() {}
    
    // prints the priority queue in order
    void print() {
      node<T> *it = head;
      while(it!=sentinel) {
        std::cout<<it->data<<"\n";
        it = it->next;
      }
    }

};
