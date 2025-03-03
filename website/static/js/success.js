document.addEventListener("alpine:init", () => {
    Alpine.data("success", () => ({
        fileUrl: "{{ file_url }}",
        copied: false,
        copyToClipboard() {
            navigator.clipboard.writeText(this.fileUrl).then(() => {
                this.copied = true;
                setTimeout(() => this.copied = false, 2000);
            });
        }
    }));
});