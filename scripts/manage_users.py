"""Local password reset utility (no plaintext password written to file)."""
import getpass, os,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from backend import security
from backend.app import db

def main():
    print('FoodRecall local training user password reset')
    username=input('User email: ').strip().lower()
    p=getpass.getpass('New password (>= 12 chars): ')
    p2=getpass.getpass('Confirm new password: ')
    if p!=p2:raise SystemExit('Passwords do not match')
    with db() as c:security.reset_password(c,username,p)
    print('Password updated; earlier sessions revoked.')
if __name__=='__main__':main()
