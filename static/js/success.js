document.addEventListener("alpine:init", () => {
    Alpine.data("success", () => ({
        fileUrl: "",
        copied: false,
        copyToClipboard() {
            navigator.clipboard.writeText(this.fileUrl).then(() => {
                this.copied = true;
                setTimeout(() => this.copied = false, 2000);
            });
        }
    }));
});