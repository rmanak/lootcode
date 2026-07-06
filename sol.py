
def medianStream(operations):
    import heapq
    # Write your solution here.
    low = []
    high = []
    res = []
    for each in operations:
        if each[0] == 'addNum':
            res.append(None)
            num = each[1]
            if len(low) == 0:
                low.append(-num)
                continue
                
            if len(high) == 0:
                if num >= -low[0]:
                    high.append(num)
                else:
                    low_val = heapq.heappop(low)
                    heapq.heappush(high, -low_val)
                    heapq.heappush(low, -num)
                continue
                    
            if num > high[0]:
                if len(high) < len(low):
                    heapq.heappush(high, num)
                else:
                    high_val = heapq.heappop(high)
                    heapq.heappush(low, -high_val)
                    heapq.heappush(high, num)
            else:
                if len(low) == len(high):
                    heapq.heappush(low, -num)
                else:
                    low_val = heapq.heappop(low)
                    heapq.heappush(high, -low_val)
                    heapq.heappush(low, -num)
        else:
            if len(low) > len(high):
                median = -low[0]
                res.append(median)
            else:
                median = (-low[0] + high[0]) / 2.0
                res.append(median)
    
    return res
            
                    
                    
                    
                    
                
