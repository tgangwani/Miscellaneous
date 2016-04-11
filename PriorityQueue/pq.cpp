#include<iostream>
#include<list>
#include"boost/program_options.hpp"
#include<pthread.h>
#include"pq.h"
#include"barrier.h"

// define type of priority queue elements
typedef uint64_t pq_element_t; 

// argument structure for each pthread
template <typename T>
struct m_pthread_arg{
  pq<T> *q_ptr;  // pointer to the priority queue
  uint32_t tid;
};

// global variables
uint32_t numThreads;
pthread_barrier_t barr;

// function to parse the input 
void parseArgs(int argc, char **argv) {
  
  namespace po = boost::program_options;
  po::options_description desc("Options"); 
  desc.add_options() 
    ("help", "Print help messages") 
    ("t", po::value<uint32_t>(&numThreads)->required(), "Number of threads");

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
  }
  catch (po::error& e)
  {
    std::cout<<"ERROR:"<<e.what()<<"\n";
    std::cout<<desc<<"\n";
    exit(1);
  }

  std::cout<<"Starting program with "<<numThreads<<" thread(s)\n";
}

// function called by each pthread
template <typename T>
void* th_fn(void *arg) {
  m_pthread_arg<T> *m_arg = (m_pthread_arg<T>*) arg;
  pq<T> *ptr = m_arg->q_ptr;
  uint32_t thread_id = m_arg->tid;

  for(uint32_t k=0; k<10; k++) {
    // dummy : each thread enqueues nodes with some values
    T data = (T)(thread_id*k+1);

    ptr->enqueue(data);
  }

  return 0;
}

int main(int argc, char **argv) {

  parseArgs(argc, argv);
 
  assert(numThreads > 0);
  std::list<pthread_t> pthreads(numThreads-1); 

  // init the priority queue
  pq<pq_element_t> Q;

  // init the pthread barrier
  if(pthread_barrier_init(&barr, NULL, numThreads)){
    std::cout<<"Could not initialize pthread barrier\n";
    exit(1);
  }
  
  // spawn numThreads-1 new threads
  uint32_t t = 0;
  for(auto &m:pthreads){
    m_pthread_arg<pq_element_t> args;
    args.q_ptr = &Q;
    args.tid = ++t;
    pthread_create(&m, NULL, &th_fn<pq_element_t>, (void*)(&args));
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
  Q.print();

  pthread_barrier_destroy(&barr);
  std::cout<<"Application complete"<<"\n";
  return 0;
}