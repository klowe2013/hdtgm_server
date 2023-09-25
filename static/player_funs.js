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
    let n_chunks = 1 // Eventually replace with some lookup logic from database
    let full_audio = ""
    console.log(`Loading episode id ${episode_id}`)
    for (i=0; i < n_chunks; i++){
        const res = await fetch(`/audio_by_id/${episode_id}`);
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

