from pyspec import *

class VerifyUserSpecification( object ):
	@context
	def setUp( self ):
		self.user = User( "Mark Dancer" )
	@spec
	def verifyInitialUserNameIsNameInConstructor( self ):
		self.shouldBeEqual( self.user.name, "Mark Dancer" )

	def verifyInitialUserHasNoLanguages( self ):
		self.shouldBeEmpty( self.user.languages )
        	
if __name__ == "__main__":
	run_test()
