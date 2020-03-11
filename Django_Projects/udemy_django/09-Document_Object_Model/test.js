function ready(fn){

    if (document.readyState !== 'loading')
        fn();
    else {
        console.log(document.readyState);
        document.addEventListener('DOMContentLoaded', fn);
    }
}

function fn(){
    console.log("done");
}

// $(document).ready(fn);

ready(fn);
// fn();

