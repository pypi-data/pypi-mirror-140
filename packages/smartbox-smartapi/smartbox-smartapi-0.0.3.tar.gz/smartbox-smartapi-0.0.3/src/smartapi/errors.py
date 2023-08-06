from graphql.error import GraphQLError

# define Python user-defined exceptions
class FriendlyError(GraphQLError):
    """Base class for Friendly Errors"""
    pass

class UnauthorizedError(GraphQLError):
    """Base class for Unauthorized Errors"""
    def __init__(self):
        super().__init__('UnauthorizedError')
    pass

class ForbidenError(GraphQLError):
    """Base class for Forbiden Errors"""
    def __init__(self):
        super().__init__('ForbidenError')

    pass
