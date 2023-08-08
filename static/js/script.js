'use strict'

async function sendRequest(companyID, userID) {
  console.log("company " + companyID);
  console.log("user " + userID);
  fetch("/stocks") // returns response to /stocks
    .then(response => {
      console.log("success");
    })
    .catch(error => { // error handling
      console.log("fail");
    });
}