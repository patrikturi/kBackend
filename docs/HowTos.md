## Performance testing
```
snap install hey
hey -n 10 -c 2 https://backend.ksoccersl.com/api/v1/users/marketplace/ -H 'Content-Type:application/json'
```
