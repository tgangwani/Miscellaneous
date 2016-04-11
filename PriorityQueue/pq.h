// implements the priority queue
#include<type_traits>
#include<atomic>
#include<assert.h>

//#define DEBUG 

// macro to check if the last bit of a 64-bit value is 0
#define CHECK_MSB(val) assert((reinterpret_cast<uintptr_t>(val) & static_cast<uintptr_t>(1)<<63) == 0);

// node type of the priority queue
template <typename T>
class node {
  public:  
    T data;
    // make sure the next pointer is 8-byte aligned
    //typename std::aligned_storage<sizeof(uintptr_t), alignof(uintptr_t)>::type next;
    node<T> *next;

    node(T& _data): data(_data), next(NULL) {}
    node(): next(NULL) {} 
};

template <typename T>
class pq {
  private:
    // (atomic) pointer to the top of the queue 
    std::atomic<node<T>*> head;
    node<T> *sentinel;

  public:
    pq() {
       // create the sentinel node that marks the end of the priority queue
       sentinel = new node<T>();
       #ifdef DEBUG
         std::cout<<"Sentinel node created at address "<<sentinel<<"\n";
       #endif 
       CHECK_MSB(sentinel); // check if the msb is zero. We'll use this for logical deletion
       head = sentinel;
    }
  
    ~pq() {
      delete sentinel;
    }

    // function to add to the priority queue
    void enqueue(T& data) {

      node<T> *new_node = new node<T>(data);
      #ifdef DEBUG
        std::cout<<"New data node created at address "<<new_node<< " with data " << data<<"\n";
      #endif
      CHECK_MSB(new_node);  // check if the msb is zero. We'll use this for logical deletion
      auto prev = &head;
      //node<T> **prev = reinterpret_cast<node<T> **> (&head);
      node<T> *curr, *next;
      int d;
  
      start:
        curr = head.load(std::memory_order_relaxed);    // load the head

      while(true){
        if(curr == sentinel) break;  

        d = (reinterpret_cast<uintptr_t>(curr->next) & (static_cast<uintptr_t>(1)<<63)) > 0 ? 1 : 0;
        next = reinterpret_cast<node<T> *> ((reinterpret_cast<uintptr_t>(curr->next) << static_cast<uintptr_t>(1)) >> static_cast<uintptr_t>(1));
        
        if(d) {
          #ifdef DEBUG
            std::cout<<"Logical bit set\n";
          #endif
          node<T> *expected = reinterpret_cast<node<T> *> ((reinterpret_cast<uintptr_t>(curr) << static_cast<uintptr_t>(1)) >> static_cast<uintptr_t>(1)); 

          if(!atomic_compare_exchange_weak_explicit(prev, &expected, next, std::memory_order_release, std::memory_order_relaxed)) {
            goto start;
          }

        }
        else {
          // found where to insert ?
          if(curr->data >= new_node->data) {
            break; 
          }
          prev = reinterpret_cast<std::atomic<node<T>*>*> (&curr->next);
        }
        #ifdef DEBUG
          std::cout<<"Priority Queue spot rejected. Trying next.\n";
        #endif
        curr = next;
      }

      // insert node between prev and curr
      new_node->next = curr;
                                                      
      node<T> *expected = reinterpret_cast<node<T> *> ((reinterpret_cast<uintptr_t>(curr) << static_cast<uintptr_t>(1)) >> static_cast<uintptr_t>(1)); 
      if(!atomic_compare_exchange_weak_explicit(prev, &expected, new_node, std::memory_order_release, std::memory_order_relaxed)) {
        goto start;
      }
      // node inserted successfully!
      #ifdef DEBUG
        std::cout<<"Node inserted successfully!\n";
      #endif
    }

    void dequeue() {}

    void print() {
      node<T> *it = head;
      while(it!=sentinel) {
        std::cout<<it->data<<"\n";
        it = it->next;
      }
    }

};
