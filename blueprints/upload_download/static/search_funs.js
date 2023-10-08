send_search = async (search_query, n_episodes=10) => {
    const params = {'search_text': search_query, 'n_results': n_episodes}
    const options = {
        'method': 'POST',
        'body': JSON.stringify(params),
        'headers': {'content-type': 'application/json'}
    }
    let res = await fetch("/search_text", options);
    return res 
}

function removeOptions(selectElement) {
    var i, L = selectElement.options.length - 1;
    for(i = L; i >= 0; i--) {
       selectElement.remove(i);
    }
 }

search_btn = document.getElementById("search-btn")
search_text = document.getElementById("search_text")
episode_selector = document.getElementById("episode_selector")
n_episodes = document.getElementById("n_episodes")
search_btn.addEventListener("click", async () => {
    removeOptions(episode_selector)
    let res = await send_search(search_text.value, n_episodes.value)
    let {episodes: episode_list} = await res.json();
    let episode_ids = Object.keys(episode_list)
    for (i=0; i < episode_ids.length; i++){
        console.log(`Adding new option: id=${episode_ids[i]}, title=${episode_list[episode_ids[i]]}`)
        let option = document.createElement("option")
        option.value = episode_ids[i]
        option.text = episode_list[episode_ids[i]]
        episode_selector.add(option)
    }
});

const form = document.querySelector('form');
form.addEventListener('submit', handleUpload);
function handleUpload(event) {
    const form = event.currentTarget;
    const formData = new FormData(form);

    const fetchOptions = {
        method: form.method,
        body: formData    
    };

    fetch('/episode_upload', fetchOptions);
  
    event.preventDefault();
  }