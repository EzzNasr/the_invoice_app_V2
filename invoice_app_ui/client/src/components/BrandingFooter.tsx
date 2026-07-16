import { Linkedin, Github, Globe } from "lucide-react";

const BrandingFooter = () => {
  return (
    <div
      style={{
        position: "fixed",
        bottom: "12px",
        right: "12px",
        display: "flex",
        gap: "12px",
        alignItems: "center",
        zIndex: 9999,
        padding: "6px 10px",
        borderRadius: "8px",
        background: "rgba(0,0,0,0.4)",
        backdropFilter: "blur(4px)",
      }}
    >
      <a href="https://www.linkedin.com/in/ezz-nasr-5a51a3368/" target="_blank" rel="noopener noreferrer">
        <Linkedin size={30} color="#fff" />
      </a>
      <a href="https://github.com/EzzNasr/" target="_blank" rel="noopener noreferrer">
        <Github size={30} color="#fff" />
      </a>
      <a href="https://ezznasr.dev" target="_blank" rel="noopener noreferrer">
        <Globe size={30} color="#fff" />
      </a>
    </div>
  );
};

export default BrandingFooter;