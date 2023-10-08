const change_btn = document.getElementById("change_button");
const play_btn = document.getElementById("play")
const ep_selector = document.getElementById("episode_selector");
const player = document.getElementById('audio_player')
const mp3_prefix = "data:audio/mp3;base64, "
let audio_buffer = ""

function delay(milliseconds){
    return new Promise(resolve => {
        setTimeout(resolve, milliseconds);
    });
}

load_audio = async (episode_id) => {
    let n_chunks = 2 // Eventually replace with some lookup logic from database
    let full_audio = ""
    console.log(`Loading episode id ${episode_id}`)
    for (i=0; i < n_chunks; i++){
        // const params = {'chunk_no': i, 'ep_id': episode_id}
        // const options = {
        //     'method': 'POST',
        //     'body': JSON.stringify(params),
        //     'headers': {'content-type': 'application/json'}
        // }
        const res = await fetch(`/audio_by_id/${episode_id}_${i}`);
        let {snd: b64buf} = await res.json();
        full_audio = full_audio + b64buf
        await delay(50)
    }
    return full_audio
}

check_player_time = () => {
    // Returns current player time in seconds (e.g., 90 = 1 min 30s)
    return player.currentTime
}

change_player_time = (delta_seconds) => {
    player.currentTime += delta_seconds
}

update_audio = (episode_id) => {
    console.log('entering update_audio')
    let is_paused = play_btn.paused 
    play_btn.innerHTML = 'Loading...'
    
    load_audio(episode_id).then(
        (res) => {
            let audio_buffer = res
            player.src = `${mp3_prefix}${audio_buffer}`
            if (is_paused) {
                play_btn.innerHTML = 'Play'
            } else {
                play_btn.innerHTML = 'Pause'
                player.play()
            }
        }
    )    
}
// update_audio = (episode_id) => {
//     console.log('entering update_audio')
//     player.src = `/stream_by_id/${episode_id}`
// }

change_btn.addEventListener("click", function () {
    console.log('received click for audio buffer')
    update_audio(ep_selector.value)
});

play_btn.addEventListener("click", function () {
    if (player.paused) {
        player.play()
        play_btn.innerHTML = 'Pause'
    } else {
        player.pause()
        play_btn.innerHTML = 'Play'
    }
})

download_curr_episode = () => {
    let episode_id = ep_selector.value 
    let episode_name = ep_selector.options[ep_selector.selectedIndex].text
    let filename = `${episode_name}.mp3`
    fetch(`/download_by_id/${episode_id}`)
        .then((res)=>{
            return res.blob()
        }).then((blob)=>{
           let el = document.createElement("a"); 
           // creates anchor element but doesn't add it to the DOM
           el.setAttribute("download", [filename]) 
           // make the link downloadable on click
           let url = URL.createObjectURL(blob); 
           // creates a url to the retrieved file
           el.href = url; // set the href attribute attribute
           el.click(); 
           URL.revokeObjectURL(url)
        })
    // catch errors
    .catch(err=>console.log(err));
}

