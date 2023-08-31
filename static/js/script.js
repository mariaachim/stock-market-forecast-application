'use strict'

async function sendRequest(companyID, userID) {
  // for debugging
  console.log("company " + companyID);
  console.log("user " + userID);
  // javascript object for JSON.stringify() function
  let obj = {};
  obj.companyID = companyID;
  obj.userID = userID;
  let resp = await fetch("/stockfavourites", { // returns response to /stocks
    credentials: "same-origin",
    mode: "same-origin",
    method: "post",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(obj) // parses data to JSON
  })
  await resp.json().then(result => {
    console.log(result);
    document.getElementById('msg').innerHTML = result.msg;
  })
}

function partition(array, low, high) {
  let pivot = array[high];
  let i = low - 1;
  for (let j = low; j < high; j++) {
    if (array[j] <= pivot) {
      i = i + 1;
      [array[i], array[j]] = [array[j], array[i]];
    }
  }
  [array[i + 1], array[high]] = [array[high], array[i + 1]];
  return i + 1;
}

function quicksort(array, low, high) {
  if (low < high) {
    let pi = partition(array, low, high);
    quicksort(array, low, pi - 1);
    quicksort(array, pi + 1, high);
  }
}

function test(data) {
  quicksort(data, 0, data.length - 1);
  console.log(data);
}