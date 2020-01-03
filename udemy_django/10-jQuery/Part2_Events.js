// jQuery makes it easy to interact with the DOM!

// List of all possible events!
// https://api.jquery.com/category/events/


// js执行顺序问题，script标签写在上边的先执行，所以你的代码要放到你引入jquery的后边，同时你这样写的话，你的js是先执行的，但是你的button这时候还不存在，你放到后边，前面的html加载完js就能找到了
// 如果你非要放在head里的话，把你的代码放到window.onload里边
// window.οnlοad=function(){
// 你的js代码
// }
// 或者用jquery的
// $(document).ready(function(){
// 你的js代码
// })

//////////////
// CLICKS ///
////////////
console.log("connected");
$(document).ready(function () {
  var h1 = $("h1");
// On Click
h1.click(function(){
  console.log("There was a click!");
});

// Click on multiple elements
$('li').click(function() {
  console.log("Click on any li !");
});

// Using This with jQuery
$('h3').click(function() {
  $(this).text("I was changed!");
});

/////////////////
// KEYPRESS ////
///////////////
// Using This with jQuery
$('input').eq(0).keypress(function() {
  $('h3').toggleClass("turnRed");
})

// We can use this event object, that has a ton of information!
$('input').eq(0).keypress(function(event) {
  console.log(event);
})

// Each Keyboard Key has a Keycode, for example Enter is 13
$('input').eq(0).keypress(function(event) {
  if(event.which === 13){
    $('h3').toggleClass("turnBlue");
  }
})

////////////
// ON() ///
//////////

// on() basically works like addEventListener()
h1.on("dblclick",function() {
  $('h1').addClass('turnBlue');
});

$('li').on('mouseenter',function() {
  $(this).toggleClass('turnRed');
});

/////////////////////////////
// EFFECTS and ANIMATIONS //
///////////////////////////

// http://api.jquery.com/category/effects/

$('input').eq(1).val("FADE OUT EVERYTHING");

// $('input').eq(1).on("click",function(){
//   $(".container").fadeOut(3000) ;
// })


$('input').eq(1).on("click",function(){
  $(".container").slideUp(1000) ;
})

});
