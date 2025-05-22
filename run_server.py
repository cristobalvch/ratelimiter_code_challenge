import time
import argparse
from fastapi import FastAPI, Request, HTTPException, status
from functools import wraps
from pydantic import BaseModel
import uvicorn



class TokenBucket:
    """
    A class implementing the Token Bucket algorithm for rate limiting.

    The token bucket allows a maximum burst of requests (capacity) and refills
    tokens over time at a fixed rate (refill_rate). Each incoming request consumes
    one token. If no tokens are available, the request is rejected.

    Attributes:
        capacity (int): The maximum number of tokens the bucket can hold.
        tokens (float): The current number of available tokens.
        refill_rate (float): The number of tokens added per second.
        last_checked (float): The last time the bucket was updated (timestamp).
    """
    
    def __init__(self, capacity: int, refill_rate: float):
        """
        Initializes the token bucket with a full set of tokens.

        Args:
            capacity (int): Maximum number of tokens (burst limit).
            refill_rate (float): Number of tokens to add per second.
        """
        self.capacity = capacity #Max burst requests
        self.tokens = capacity #start with full tokens in bucket
        self.refill_rate = refill_rate #tokens  added to the bucket per second
        self.last_checked = time.time() #calculate the time when the last request was made

    def allow_request(self):
        """
        Determines whether a request is allowed under the current token count.
        Refills tokens based on the time elapsed since the last check.
        
        Returns:
            bool: True if the request is allowed, False otherwise.
        """
        now = time.time()
        elapsed = now - self.last_checked #cqlculate elapsed time
        self.last_checked = now 
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate) #use the elapsed time to refill the tokens
        if self.tokens >= 1: #check if there are tokens available
            self.tokens -= 1 
            return True
        return False 


    def update_config(self, capacity, refill_rate):
        """
        Updates the configuration of the token bucket at runtime.

        Args:
            capacity (int): New capacity of the bucket.
            refill_rate (float): New refill rate (tokens per second).

        Notes:
            Ensures current token count does not exceed the new capacity.
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = min(self.tokens, self.capacity) #Ensures current tokens don’t exceed the new capacity.


class RateLimiter:
    """
    A class that applies token bucket-based rate limiting to FastAPI endpoints.

    This class wraps route handler functions with a decorator that checks whether
    the request is allowed based on the current state of a TokenBucket instance.
    """
    
    def __init__(self, bucket: TokenBucket):
        """
        Initializes the RateLimiter with a given token bucket.

        Args:
            bucket (TokenBucket): The token bucket used to track request limits.
        """
        
        self.bucket = bucket #associate the bucket with the token bucket algorithm
    

    def rate_limited(self):
        """
        Decorator to apply rate limiting to a FastAPI route.

        Returns:
            Callable: A decorator that wraps the endpoint function and enforces
            rate limiting using the associated TokenBucket.
        """
        def decorator(func):
            @wraps(func)
            async def wrapper(request: Request, *args, **kwargs):
                if not self.bucket.allow_request(): 
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail="Rate limit exceeded. Try again later."
                    )
                return await func(request, *args, **kwargs)
            return wrapper
        return decorator


class RateLimitUpdate(BaseModel):
    """
    Pydantic model for updating the token bucket configuration via API.

    Attributes:
        capacity (int): Maximum number of tokens in the bucket.
        refill_rate (float): Number of tokens added to the bucket per second.
    """
    capacity: int
    refill_rate: float
    
    

def create_app(capacity: int, refill_rate: float) -> FastAPI:
    """
    Creates and configures a FastAPI app with rate-limited routes.

    Args:
        capacity (int): The token bucket's maximum capacity.
        refill_rate (float): Token refill rate per second.

    Returns:
        FastAPI: The configured FastAPI application.
    """
    app = FastAPI()
    bucket = TokenBucket(capacity, refill_rate)
    rate_limiter = RateLimiter(bucket)
    @app.get("/")
    @rate_limiter.rate_limited()
    async def rate_limited_endpoint(request: Request):
        """
        A sample endpoint that is protected by rate limiting.

        Returns:
            dict: A JSON response indicating successful access.
        """
        return {"message": "Rate Limiter Code Challenge!"}
    
    
    @app.post("/update")
    async def update_rate_limit(config: RateLimitUpdate):
        """
        Updates the rate limit configuration via API.

        Args:
            config (RateLimitUpdate): New values for capacity and refill rate.

        Returns:
            dict: Confirmation message and new configuration.
        """
        bucket.update_config(config.capacity, config.refill_rate)
        return {
            "message": "Rate limit updated",
            "new_config": {"capacity": config.capacity, "refill_rate": config.refill_rate}
        }

    return app

def args_handler():
    """
    Parses command-line arguments for capacity and refill rate.
    Returns:
        argparse.Namespace: Parsed arguments with capacity and refill_rate.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--capacity", type=int, default=5)
    parser.add_argument("--refill_rate", type=float, default=0.5)
    args = parser.parse_args()
    return args


def main():
    args = args_handler()
    app = create_app(args.capacity, args.refill_rate)
    uvicorn.run(app, host="127.0.0.1", port=8000)

if __name__ == "__main__":
    main()