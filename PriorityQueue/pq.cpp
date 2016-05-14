#include<time.h>
#include<algorithm>
#include<pthread.h>
#include"boost/program_options.hpp"
#include"pq.h"
#include"barrier.h"
#include"m5op.h"

// when enabled, the program stores the 'data' that was added or removed at
// each enqueue() and deleteMin() call. This data can be used to implement
// application specific logic 
//#define USE_APP  

// define type of priority queue elements
typedef uint64_t pq_element_t; 

// argument structure for each pthread
template <typename T>
struct m_pthread_arg{
  pq<T> *q_ptr;  // pointer to the priority queue
  uint32_t tid;
};

// function to parse the input 
void parseArgs(int argc, char **argv) {
  
  namespace po = boost::program_options;
  po::options_description desc("Options"); 
  desc.add_options() 
    ("help", "Print help messages") 
    ("t", po::value<uint32_t>(&numThreads)->required(), "Number of threads")
    ("m", po::value<uint64_t>(&numNodes)->default_value(10000), "Number of nodes by each thread")
    ("hb", "Enable heartbeating");

  po::variables_map vm; 
  try 
  {
    po::store(po::parse_command_line(argc, argv, desc), vm);
    po::notify(vm);
    if(vm.count("help"))
    {   
      std::cout<<desc<<"\n";
      exit(1);
    }   
    if(vm.count("hb"))
    {
      heartbeat =true;
    }
  }
  catch (po::error& e)
  {
    std::cout<<"ERROR:"<<e.what()<<"\n";
    std::cout<<desc<<"\n";
    exit(1);
  }

  std::cout<<"Starting program with "<<numThreads<<" thread(s). Each thread inserts " << numNodes << " nodes.\n";
}

// prints the final stats for the application
void print_stats() {
  std::cout<<"+++Stats+++\n";
  for(uint8_t i = 0; i < NUM_STATS; i++) {
    std::cout<<stat_map[i]<<"\t"<<final_stats[i]<<"\n";
  }
}

// per-thread stat collection
void collect_stats() {
  for(uint8_t i = 0; i < NUM_STATS; i++) {
    final_stats[i].fetch_add((*stats.get())[i]);
  }
}

// function called by each pthread
template <typename T>
void* th_fn(void *arg) {
  m_pthread_arg<T> *m_arg = (m_pthread_arg<T>*) arg;
  pq<T> *ptr = m_arg->q_ptr;
  uint32_t thread_id = m_arg->tid;
  std::vector<T> enq_removals, deq_removals;  // data items removed from queue during enqueue/deleteMin
  std::vector<T> enq_adds;
  stats.reset(new std::vector<uint64_t>(NUM_STATS, 0)); // thread-local-storage

  // wait for all threads to reach this point
  pthread_barrier_wait(&barr);

  #ifdef USE_APP
    // reserve capacities for fast push_back
    enq_removals.reserve(numNodes);
    deq_removals.reserve(numNodes);
    enq_adds.reserve(numNodes);
  #endif

  for(uint32_t k=0; k<numNodes; k++) {
    
    // generate random priorities in (1, 100) 
    T data = (T)(rand()%100 + 1);
    ptr->enqueue(data, thread_id, enq_removals, enq_adds);
    ptr->deleteMin(thread_id, deq_removals);

    // periodic heartbeats from thread-0
    if(heartbeat && thread_id == 0 && k%1000 == 0) {
      std::cout<<"[Heartbeat] Completed " << k << " nodes.\n";
    }
  }

  // boost thread-safe logging
  //BOOST_LOG_TRIVIAL(debug) << "[end] " << enq_removals.size() + deq_removals.size() << "\n"; 
  //BOOST_LOG_TRIVIAL(debug) << enq_adds.size();
  collect_stats();
  return 0;
}

int main(int argc, char **argv) {

  parseArgs(argc, argv);

  srand (time(NULL));

  assert(numThreads > 0);
  std::list<pthread_t> pthreads(numThreads-1); 
  std::vector<m_pthread_arg<pq_element_t> > args_list(numThreads-1); 

  // init the priority queue
  pq<pq_element_t> Q;
  
  // init the pthread barrier
  if(pthread_barrier_init(&barr, NULL, numThreads)){
    std::cout<<"Could not initialize pthread barrier\n";
    exit(1);
  }
  
  // simulation marker (roi-begin)
  m5_work_begin(0, 0);

  // spawn numThreads-1 new threads
  uint32_t t = 1;
  for(auto &m:pthreads){
    args_list[t-1].q_ptr = &Q;
    args_list[t-1].tid = t;
    pthread_create(&m, NULL, &th_fn<pq_element_t>, (void*)(&(args_list[t-1])));
    ++t;
  }

  // assign work to thread-0
  m_pthread_arg<pq_element_t> args;
  args.q_ptr = &Q;
  args.tid = 0;
  th_fn<pq_element_t>((void*)&args);

  for(auto &m:pthreads){
    pthread_join(m, NULL);
  }

  // prints the priority queue
  //Q.print();
  print_stats();
  
  // simulation marker (roi-end)
  m5_work_end(0, 0);


  pthread_barrier_destroy(&barr);
  std::cout<<"Application complete"<<"\n";
  return 0;
}
