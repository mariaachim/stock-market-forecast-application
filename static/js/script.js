'use strict'

async function send_request(company_id, user_id) {
  // for debugging
  console.log("company " + company_id);
  console.log("user " + user_id);
  // javascript object for JSON.stringify() function
  let obj = {};
  obj.company_id = company_id;
  obj.user_id = user_id;
  let resp = await fetch("/stock_favourites", { // returns response to /stocks
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