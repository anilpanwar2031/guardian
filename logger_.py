import logging
import time
def setup_logging(name="logger",
                  filepath=None,
                  stream_log_level="",
                  file_log_level=""):
    
    logging.basicConfig(filename=filepath, filemode='w', format='%(name)s -%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    return logger


logger = setup_logging(name="default_log",filepath="logger.log")




def log_decorator(log_name):
    def log_this(function):
        logger = logging.getLogger(log_name)
        
        
        def new_function(*args,**kwargs):
            time1 = time.time()
          #  logger.debug(f"{function.__name__} - {args} - {kwargs}")
            logger.info(f"{function.__name__}       - {args[0].__str__()} - {kwargs}")
            output = function(*args,**kwargs)
            time2 = time.time()
            logger.info(f"{function.__name__}        Time Taken-          {int(time2-time1)}")
            
            #logger.debug(f"{function.__name__} returned: {output}")
            
            

            return output
        return new_function
    return log_this