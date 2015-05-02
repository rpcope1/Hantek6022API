__author__ = 'Robert Cope'

from PyHT6022Scope.app import ScopeApp

scope_app = ScopeApp()
if scope_app.initial_setup():
    scope_app.mainloop()