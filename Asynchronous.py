import asyncio
import time

#? Async Def or Function are also called as "co-routine"
#? Asynchronous is Con-currency and not Multi-tasking or Multi-threading
'''Event Loop:
An event loop is a loop that can register tasks to be executed. execute them, delay or even
cancel them and handle different events related to these operations. Generally. we schedule
multiple async functions to the event The loop runs one function. while that function
waits for 10, it pauses it and runs another.
'''
'''Bloacking:
A synchronous operation blocks a process till the operation completes. An asynchronous operation is non-blocking and only initiates the operation.
'''

##************* 1 ****************
async def main_1():
    ''' This is not really async programming because "await" means wait for a task to complete, 
    hence " await asyncio.sleep(2) " is same as regular syncronous: " time.sleep(2) " .
    ? Question is, then why don't we simply use - regular syncronous: " time.sleep(2) ", instead of - " await asyncio.sleep(2) " ?
    >> The point is, we can use "await" to make synchronous calls in an async function.    
    '''
    print('A')
    await asyncio.sleep(2)  # time.sleep(2)
    print('B')
    
# >> A, B

##************* 2 ****************
async def main_2():
    print('A')
    await otherFunc()       #* Notice it is "waiting" for otherFunc() to complete, hence this script is same synchronous programming
    print('B')

async def otherFunc():
    print(1)
    await asyncio.sleep(2)
    print(2)

# >> A, 1, 2, B
 
##************* 3 ****************
async def main_3():
    ''' Now we are creating a task, and this is true Asynchronous Program.
    Becuase now when it finds "await" anywhere in otherFunc() it will return and start doing other tasks.
    It will go to complete the async task only when it finds "Idle time".
    
    IMPORTANT: When it finds "await" anywhere in otherFunc() it will return and start doing other tasks,
    but if you don't await for a create task to complete, the program will ignore it and terminate.
    So here, we are creating a task for otherFunc(), hence the otherFunc() will only execute when it finds that "Idle time",
    and in this case it will find that time at the end i.e., after printing 'A' and 'B'.
    But the catch is, it will only print 1 from otherFunc() and ignore all other tasks of otherFunc(), because as soon as it finds "await"
    it will return and try to execute other tasks, but as there is no other task to execute, it will just terminate.
    But as we also want the otherFunc() to complete, we need to wait for it. (see next Ex)
    '''
    task = asyncio.create_task(otherFunc())
    print('A')
    print('B')

async def otherFunc():
    print(1)
    await asyncio.sleep(2)
    print(2)
    
# >> A, 1, B   

##***** Ex ********
# async def foo():
#     print('Hi')
# print(foo())  # Check it just have an async object. But will not execute, because foo() is an async function, and is never "awaited", hence the function is ignored!!

##************* 4 ****************
async def main_4():
    task = asyncio.create_task(otherFunc())
    print('A')
    print('B')
    await task      #* Now it will also await for task to complete
    ''' But the use of Asynchronous Function is still not clear, Right? Check out the next Ex.'''

async def otherFunc():
    print(1)
    await asyncio.sleep(2)
    print(2)

# >> A, B, 1, 2

##************* 5 ****************
async def main_5():
    ''' Flow: 
    1. Print 'A'
    2. finds "await" -- Idle time, hence go for any "previous" remaining execution "if available" -- Here call otherFunc()
    3. Print 1
    4. finds "await" -- Idle time, hence go for any "previous" remaining execution "if available" -- Here printing 'B'
    5. finds "await" -- Idle time, hence go for any "previous" remaining execution "if available" -- Here No other possible executions, hence just wait for "task"
    '''
    task = asyncio.create_task(otherFunc())
    print('A')
    await asyncio.sleep(1)
    print('B')
    await task

async def otherFunc():
    print(1)
    await asyncio.sleep(2)
    print(2)

# >> A, 1, B, 2
  
##************* 6 ****************
async def main_6():
    ''' Flow: 
    1. Print 'A'
    2. finds "await" -- call otherFunc()
    3. Print 1
    4. finds "await" -- 
        Here the previous task i.e., sleep(6) is still not completed,hence we have to wait.
        But as we are waiting, meanwhile sleep(2) will be completed in otherFunc(), hence we go back and try to execute the next task i.e., print 2.
        And finally, now we don't have any other task, hence we have to wait for the sleep(6) to complete.
    5. Print 'B'
    '''
    task = asyncio.create_task(otherFunc())
    print('A')
    await asyncio.sleep(6)      #* We increased the waiting time
    print('B')
    await task

async def otherFunc():
    print(1)
    await asyncio.sleep(2)
    print(2)

# >> A, 1, 2, B
    
##************* 7 ****************
async def main_7():
    ''' Flow: 
    1. Print 'A'
    2. finds "await" -- call otherFunc()
    3. Print 1
    4. finds "await" -- sleep(6) is still not completed, meanwhile sleep(2) will be completed in otherFunc(), print 2.
        Here the otherFunc() is end, yet it will return only when the task is awaited, this return is called "Future" or "Promise".
    5. Print 'B'
    6. Print return value (Future)
    '''
    task = asyncio.create_task(otherFunc())
    print('A')
    await asyncio.sleep(6)
    print('B')
    val = await task                #* Future / Promise
    print(val)
    
async def otherFunc():
    print(1)
    await asyncio.sleep(2)
    print(2)
    return 9999
    
# >> A, 1, 2, B, 9999

##************* 8 ****************
import asyncio
async def foo2():
    print('Hi')
# foo2()                            #* ofcourse this will ignore the function entirely as never awaited.
# await foo2()                      #* This should've worked in an async function, but "await" can't be outside of an async function.
# asyncio.run(foo2())               #* To call an async function outside. We need to make "Async Event Loop". So the co-routines can be placed in this event loop.
# loop = asyncio.get_event_loop()   #* Or this to make event loop event loop.
# loop.run_until_complete(foo2())
# loop.close()

##************* 9 ****************
async def f():
    print("start fetching")
    await asyncio.sleep(2)
    print("Finish fetching")
    return 2000

async def n():
    for i in range(1, 100):
        print(i)
        await asyncio.sleep(0.25)

async def main_8():
    '''
    Flow:::
    - task1 created
    - task2 created
    - print(async object)
    - main() function ended -- now has idle time
    - task1 started and printed "start fetching", found "await", hence return to main() for another task to execute in the mean time
    - task2 started and printed "1", found "await", hence return to main() for another task to execute in the mean time
    - No another task found.
    - task1 and task2 never awated hence ignored
    - Terminate main()
    '''
    task1 = asyncio.create_task(f())
    task2 = asyncio.create_task(n())
    
    value = await task1
    print(value)    # This will only have async object, no Future


#? CALL MAIN
if __name__ == '__main__':
    asyncio.run(main_8())




'''
Example: API requests Asynchronously
'''

#********************** Synchronous *********************
import time
import requests

AlphaVanAPI = "DT19A4RWPMR4YWZ3"
url = "https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={}&interval=5min&apikey={}"
symbols = ['AAPL', 'GOOG', 'TSLA', 'MSFT', 'XOM', 'WMT', 'PFE', 'HBC', 'JNJ', 'BAC']
results = []

print('Started Requesting!')
start = time.time()

def reqAPI():
    for symbol in symbols:
        print('Requesting for {}'.format(symbol))
        response = requests.get(url=url.format(symbol, AlphaVanAPI))
        results.append(response.json())

reqAPI()

end = time.time() - start
print('Done Requesting! Took {} seconds'.format(end))


#********************** A-Synchronous *********************
import time
import asyncio
# import requests # requests module is naturally synchronous, hence we need an async module - aiohttp
import aiohttp

AlphaVanAPI = "DT19A4RWPMR4YWZ3"
url = "https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={}&interval=5min&apikey={}"
symbols = ['AAPL', 'GOOG', 'TSLA', 'MSFT', 'XOM', 'WMT', 'PFE', 'HBC', 'JNJ', 'BAC']
results = []

print('Started Requesting!')
start = time.time()

''' This is improving time, but still this is another synchronous programming'''
async def reqAPI():
    async with aiohttp.ClientSession() as session:
        for symbol in symbols:
            print('Requesting for {}'.format(symbol))
            response = await session.get(url=url.format(symbol, AlphaVanAPI), ssl=False)
            results.append(await response.json())   # here we used await becuase "response" is an "awaitable object", else it will throw, RuntimeWarning: coroutine 'ClientResponse.json' was never awaited

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy()) # This is just to solve the "Event Close" error on windows
asyncio.run(reqAPI())

end = time.time() - start
print('Done Requesting! Took {} seconds'.format(end))


#********************** A-Synchronous v2 *********************
import time
import asyncio
import aiohttp

AlphaVanAPI = "DT19A4RWPMR4YWZ3"
url = "https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={}&interval=5min&apikey={}"
symbols = ['AAPL', 'GOOG', 'TSLA', 'MSFT', 'XOM', 'WMT', 'PFE', 'HBC', 'JNJ', 'BAC']
results = []

print('Started Requesting!')
start = time.time()

def get_tasks(session):
    tasks = []
    for symbol in symbols:
        tasks.append(session.get(url=url.format(symbol, AlphaVanAPI), ssl=False))  # Notice we are not "awaiting", we are just adding all sessions to "tasks"
    return tasks
        
async def reqAPI():
    async with aiohttp.ClientSession() as session:
        tasks = get_tasks(session)
        responses = await asyncio.gather(*tasks)    # gather: Return a Future aggregating results from the given coroutines/futures. '*' is for Dereferencing
        for response in responses:
            results.append(await response.json())
        
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
asyncio.run(reqAPI())

end = time.time() - start
print('Done Requesting! Took {} seconds'.format(end))


#********************** A-Synchronous v3 *********************
import time
import asyncio
import aiohttp

AlphaVanAPI = "DT19A4RWPMR4YWZ3"
url = "https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={}&interval=5min&apikey={}"
symbols = ['AAPL', 'GOOG', 'TSLA', 'MSFT', 'XOM', 'WMT', 'PFE', 'HBC', 'JNJ', 'BAC']
results = []

print('Started Requesting!')
start = time.time()

def get_tasks(session):
    tasks = []
    for symbol in symbols:
        tasks.append(asyncio.create_task(session.get(url=url.format(symbol, AlphaVanAPI), ssl=False)))   #* we are directly putting sessions in event loop here itself
    return tasks
        
async def reqAPI():
    async with aiohttp.ClientSession() as session:
        tasks = get_tasks(session)
        responses = await asyncio.gather(*tasks)    #* gather: So as we have already thrown all the sessions on the Event loop above, so it will not throw it again. Now only job for gather is to await and Return a Future aggregating results
        for response in responses:
            results.append(await response.json())
        
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
asyncio.run(reqAPI())

end = time.time() - start
print('Done Requesting! Took {} seconds'.format(end))


#********************** A-Synchronous (for single request) *********************
import time
import asyncio
import aiohttp

AlphaVanAPI = "DT19A4RWPMR4YWZ3"
url = "https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={}&interval=5min&apikey={}"
symbol = 'AAPL'

print('Started Requesting!')
start = time.time()

async def reqAPI():
    async with aiohttp.ClientSession() as session:
        task = asyncio.create_task(session.get(url=url.format(symbol, AlphaVanAPI), ssl=False))
        response = await task
        return await response.json()
        
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
print(asyncio.run(reqAPI()))

end = time.time() - start
print('Done Requesting! Took {} seconds'.format(end))

