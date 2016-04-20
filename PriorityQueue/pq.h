// implements the priority queue
#include<iostream>
#include<list>
#include<vector>
#include<atomic>
#include<assert.h>
#include"boost/log/trivial.hpp"
#include "boost/thread/tss.hpp"
#include"utils.h"

//#define DEBUG 
#define ONE static_cast<uintptr_t>(1) 
#define ONE_MSB ONE<<63 
#define RC(val) reinterpret_cast<uintptr_t>(val) 

// macro to assert if the last bit of a pointer is 0
#define CHECK_MSB(val) assert((RC(val) & ONE_MSB) == 0);

// global- variables
uint32_t numThreads = 0; 
pthread_barrier_t barr;
uint64_t numNodes = 0;
boost::thread_specific_ptr<std::vector<uint64_t>> stats;
std::vector<std::atomic<uint64_t>> final_stats(NUM_STATS);
bool heartbeat = false;

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
    void enqueue(T& data, const uint32_t& thread_id, std::vector<T>& enq_removals, std::vector<T>& enq_adds) {

      // create new node. Assert that the msb is zero. We'll use this for
      // logical deletion
      node<T> *new_node = new node<T>(data);
      CHECK_MSB(new_node);
      
      #ifdef DEBUG
        std::cout<<"New data node created at address "<<new_node<< " with data " << data<<"\n";
      #endif
      
      node<T> *curr, *next;
      bool d; // logically deleted node
  
      start:
        curr = head.load(std::memory_order_relaxed);    // load the head
        auto prev = &head;

      while(true){
        if(curr == sentinel) break;  // we have reached the end of the priority queue 

        // get the <next, d> pair from curr->next
        next = curr->next;
        d = (RC(next) & ONE_MSB) >> 63;  //  check if the msb (logical deletion bit) is set
        next = reinterpret_cast<node<T> *> ((RC(next) << ONE) >> ONE);  // remove the msb to fetch next pointer from curr->next
        
        if(d) {

          #ifdef DEBUG
            std::cout<<"Logical bit set\n";
          #endif
            
          // if the logical bit is set, try to physically remove this node from
          // the priority queue using CAS
          if(atomic_compare_exchange_weak_explicit(prev, &curr, next, std::memory_order_release, std::memory_order_relaxed)) {

            #ifdef STATS
              (*stats.get())[ENQ_STEAL_SUCC]++; 
            #endif

            #ifdef USE_APP
              enq_removals.push_back(curr->data);
            #endif

          }
          else {
            
            #ifdef STATS
              (*stats.get())[ENQ_STEAL_FAIL]++;
            #endif  

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
      // insert node between prev and curr
      if(atomic_compare_exchange_weak_explicit(prev, &curr, new_node, std::memory_order_release, std::memory_order_relaxed)) {

        #ifdef USE_APP
          enq_adds.push_back(new_node->data);
        #endif
        
        #ifdef STATS
          (*stats.get())[ENQ_SUCC]++;
        #endif  
      }
      else {

        #ifdef STATS
          (*stats.get())[ENQ_FAIL]++;
        #endif  
        
        // enqueue failed. Try again!
        goto start;
      }

      #ifdef DEBUG
        std::cout<<"Node inserted successfully!\n";
      #endif
    }

    // function to remove the top of the priority queue
    void deleteMin(const uint32_t& thread_id, std::vector<T>& deq_removals) {
      
      while(true) {
        node<T> *first = head.load(std::memory_order_relaxed);    // load the head

        if(first == sentinel) {
          // no elements in the priority queue
          break;
        }

        if(tryRemove(first, deq_removals, thread_id)) {
          break;
        } 

      }  // while

    }

    // function return true if the thread could logically remove a node 
    bool tryRemove(node<T> *first, std::vector<T>& deq_removals, const uint32_t& thread_id) {

      // get the <next, d> pair from first->next
      node<T> *next = first->next;
      bool d = (RC(next) & ONE_MSB) >> 63;  
      next = reinterpret_cast<node<T> *> ((RC(next) << ONE) >> ONE);
  
      // is first already logically deleted?
      if(d) {

        #ifdef DEBUG
          std::cout<<"First already logically deleted\n";
        #endif

        // try to physically remove this node using CAS
        if(atomic_compare_exchange_weak_explicit(&head, &first, next, std::memory_order_release, std::memory_order_relaxed)) {
          #ifdef USE_APP
            deq_removals.push_back(first->data);
          #endif

          #ifdef STATS
            (*stats.get())[DEQ_STEAL_SUCC]++;
          #endif  
        }
        #ifdef STATS
        else {
          (*stats.get())[DEQ_STEAL_FAIL]++;  
        }
        #endif
         
        return false;
      }

      // logically delete first
      node<T> *updated_next =  reinterpret_cast<node<T> *> (RC(next) | ONE_MSB);
      auto n = reinterpret_cast<std::atomic<node<T>*>*> (&first->next);

      if(!atomic_compare_exchange_weak_explicit(n, &next, updated_next, std::memory_order_release, std::memory_order_relaxed)) {

        #ifdef STATS
          (*stats.get())[DEQ_LOG_FAIL]++;
        #endif

        // logical deletion failure
        return false;
      }
      #ifdef STATS
      else {
        (*stats.get())[DEQ_LOG_SUCC]++;
      }
      #endif
      
      // try physical removal
      if(atomic_compare_exchange_weak_explicit(&head, &first, next, std::memory_order_release, std::memory_order_relaxed)) {
        #ifdef USE_APP
          deq_removals.push_back(first->data);
        #endif
        
        #ifdef STATS
          (*stats.get())[DEQ_PHY_SUCC]++;
        #endif
      }
      #ifdef STATS
      else {
        (*stats.get())[DEQ_PHY_FAIL]++;
      }
      #endif
 
      // logical deletion success
      return true;
    }
  
    // prints the priority queue in order
    void print() {
      node<T> *it = head;
      while(it!=sentinel) {
        std::cout<<it->data<<"\n";
        it = it->next;
      }
    }

};
