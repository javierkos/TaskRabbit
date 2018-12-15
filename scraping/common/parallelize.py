from multiprocessing import Pool, cpu_count

'''
    Wrapper class to run functions concurrently
'''

class Parallelizer:

    def __init__(self, tasks):
        self.tasks = tasks


    def run_concurrent(self, task_keys, pool_size):
        with Pool(pool_size) as p:
            [p.apply_async(self.tasks[task_key]["func"], args=self.tasks[task_key]["args"]) for task_key in task_keys]
            p.close()
            p.join()
