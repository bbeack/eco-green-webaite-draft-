import { addPropertyControls, ControlType } from "framer"
import type { CSSProperties } from "react"
import { useEffect, useState } from "react"
// The single shared module. If Framer reports that it cannot resolve this
// import, add or remove the ".tsx" extension to match your project's
// convention — that is the only line that ever needs changing.
import { useRootstock, assets, type Theme } from "./Rootstock"

interface NavLink {
    label: string
    link: string
}

const DEFAULT_LINKS: NavLink[] = [
    { label: "Home", link: "" },
    { label: "Our Farm", link: "" },
    { label: "Projects", link: "" },
    { label: "Get Involved", link: "" },
    { label: "Contact", link: "" },
]

interface Props {
    theme?: Theme
    brandFont?: boolean
    sticky?: boolean
    logo?: string
    brandName?: string
    brandKicker?: string
    links?: NavLink[]
    ctaLabel?: string
    ctaLink?: string
    showThemeToggle?: boolean
    style?: CSSProperties
}

/**
 * Rootstock site header: brand, centred navigation and a single lime call to
 * action. Set Sticky off to place it in a normal Framer stack.
 *
 * @framerSupportedLayoutWidth any
 * @framerSupportedLayoutHeight fixed
 * @framerIntrinsicWidth 1440
 * @framerIntrinsicHeight 78
 */
export default function SiteHeader(props: Props) {
    const {
        theme = "auto",
        brandFont = true,
        sticky = true,
        logo = "",
        brandName = "Rootstock",
        brandKicker = "Farm & Forest",
        links = DEFAULT_LINKS,
        ctaLabel = "Plant a tree",
        ctaLink = "",
        showThemeToggle = true,
        style,
    } = props
    const wrapper = useRootstock(theme, brandFont)
    const [stuck, setStuck] = useState(false)
    const [open, setOpen] = useState(false)
    const [dark, setDark] = useState(theme === "dark")

    useEffect(() => {
        if (!sticky) return
        const onScroll = () => setStuck(window.scrollY > 24)
        onScroll()
        window.addEventListener("scroll", onScroll, { passive: true })
        return () => window.removeEventListener("scroll", onScroll)
    }, [sticky])

    useEffect(() => {
        const onKey = (e: KeyboardEvent) => e.key === "Escape" && setOpen(false)
        document.addEventListener("keydown", onKey)
        return () => document.removeEventListener("keydown", onKey)
    }, [])

    const resolvedTheme: Theme = showThemeToggle ? (dark ? "dark" : "light") : theme

    return (
        <div {...wrapper} data-theme={resolvedTheme} style={{ ...style, position: "relative" }}>
            <header className={`header${stuck ? " is-stuck" : ""}`} style={sticky ? undefined : { position: "static" }}>
                <div className="header-inner">
                    <a className="brand" href="#" aria-label={`${brandName} — home`}>
                        <img src={logo || assets.logo} alt="" width={32} height={32} />
                        <span className="brand-name">
                            {brandName}
                            {brandKicker ? <small>{brandKicker}</small> : null}
                        </span>
                    </a>

                    <nav className="nav" aria-label="Primary">
                        {links.map((item, i) => (
                            <a key={i} href={item.link || "#"}>
                                {item.label}
                            </a>
                        ))}
                    </nav>

                    <div className="header-actions">
                        {showThemeToggle ? (
                            <button
                                className="theme-toggle"
                                type="button"
                                onClick={() => setDark((d) => !d)}
                                aria-pressed={dark}
                                aria-label={dark ? "Switch to light theme" : "Switch to dark theme"}
                            >
                                {dark ? <MoonIcon /> : <SunIcon />}
                            </button>
                        ) : null}
                        {ctaLabel ? (
                            <a className="btn btn-accent btn-sm hide-md" href={ctaLink || "#"}>
                                {ctaLabel} <ArrowIcon className="btn-ico" size={15} />
                            </a>
                        ) : null}
                        <button
                            className="burger"
                            type="button"
                            aria-expanded={open}
                            aria-label={open ? "Close menu" : "Open menu"}
                            onClick={() => setOpen((o) => !o)}
                        >
                            <span />
                            <span />
                            <span />
                        </button>
                    </div>
                </div>
            </header>

            <div className={`drawer${open ? " is-open" : ""}`} aria-hidden={!open}>
                <nav aria-label="Mobile">
                    {links.map((item, i) => (
                        <a key={i} href={item.link || "#"} onClick={() => setOpen(false)}>
                            {item.label}
                            <span>{String(i + 1).padStart(2, "0")}</span>
                        </a>
                    ))}
                </nav>
                <div className="drawer-foot">
                    {ctaLabel ? (
                        <a className="btn btn-accent btn-block" href={ctaLink || "#"}>
                            {ctaLabel} <ArrowIcon className="btn-ico" size={16} />
                        </a>
                    ) : null}
                </div>
            </div>
        </div>
    )
}


addPropertyControls(SiteHeader, {
    theme: {
        type: ControlType.Enum,
        title: "Theme",
        options: ["auto", "light", "dark"],
        optionTitles: ["Auto", "Light", "Dark"],
        defaultValue: "auto",
    },
    sticky: { type: ControlType.Boolean, title: "Sticky", defaultValue: true },
    logo: { type: ControlType.Image, title: "Logo" },
    brandName: { type: ControlType.String, title: "Brand", defaultValue: "Rootstock" },
    brandKicker: { type: ControlType.String, title: "Kicker", defaultValue: "Farm & Forest" },
    links: {
        type: ControlType.Array,
        title: "Nav",
        defaultValue: DEFAULT_LINKS,
        control: {
            type: ControlType.Object,
            controls: {
                label: { type: ControlType.String, title: "Label", defaultValue: "Link" },
                link: { type: ControlType.Link, title: "Link" },
            },
        },
    },
    ctaLabel: { type: ControlType.String, title: "CTA", defaultValue: "Plant a tree" },
    ctaLink: { type: ControlType.Link, title: "CTA link" },
    showThemeToggle: { type: ControlType.Boolean, title: "Theme toggle", defaultValue: true },
    brandFont: {
        type: ControlType.Boolean,
        title: "Brand font",
        defaultValue: true,
        description: "Uses the bundled Plus Jakarta Sans. Turn off to inherit the Framer project's font.",
    },
})

/* ---------------------------------------------------------------- icons --- */
function ArrowIcon({ size = 16, className = "" }: { size?: number; className?: string }) {
    return (
        <svg className={`ico ${className}`} width={size} height={size} viewBox="0 0 24 24" fill="none"
            stroke="currentColor" strokeWidth={1.75} strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <path d="M5 12h14M13 6l6 6-6 6" />
        </svg>
    )
}
function SunIcon() {
    return (
        <svg className="ico" width={18} height={18} viewBox="0 0 24 24" fill="none" stroke="currentColor"
            strokeWidth={1.75} strokeLinecap="round" aria-hidden="true">
            <circle cx="12" cy="12" r="4.2" />
            <path d="M12 2v2.5M12 19.5V22M4.2 4.2l1.8 1.8M18 18l1.8 1.8M2 12h2.5M19.5 12H22M4.2 19.8 6 18M18 6l1.8-1.8" />
        </svg>
    )
}
function MoonIcon() {
    return (
        <svg className="ico" width={18} height={18} viewBox="0 0 24 24" fill="none" stroke="currentColor"
            strokeWidth={1.75} strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <path d="M21 13.2A9 9 0 1 1 10.8 3a7 7 0 0 0 10.2 10.2Z" />
        </svg>
    )
}
