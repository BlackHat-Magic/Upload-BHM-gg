document.addEventListener ("alpine:init", () => {
    Alpine.data ("main", () => ({
        file: null,
        modal: false,
        parse () {
            file = event.target.files[0];
            if(file.size > 1 * 1024 * 1024 * 1024) {
                this.modal = true;
                event.target.value = null;
            }
        },
    }))
})