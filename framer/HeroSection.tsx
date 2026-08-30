import { addPropertyControls, ControlType } from "framer"
import type { CSSProperties } from "react"
// The single shared module. If Framer reports that it cannot resolve this
// import, add or remove the ".tsx" extension to match your project's
// convention — that is the only line that ever needs changing.
import { useSection, useEmailCapture, assets, type Theme } from "./Rootstock"

interface Stat {
    value: string
    label: string
    tint: boolean
}
interface FloatCard {
    image: string
    title: string
    body: string
}

const DEFAULT_BODY =
    "Rootstock is a 240-acre farm in the Welsh borders. Every vegetable box we sell and every pound you give funds native woodland — planted by hand, monitored for three years, protected for a century."

const DEFAULT_STATS: Stat[] = [
    { value: "412,000+", label: "Trees planted", tint: false },
    { value: "1,840", label: "Acres restored", tint: false },
    { value: "96", label: "Partner farms", tint: false },
    { value: "100%", label: "To planting", tint: true },
]

const DEFAULT_CARDS: FloatCard[] = [
    { image: "", title: "Our nursery", body: "90,000 native saplings raised on-farm each year" },
    { image: "", title: "Living soil", body: "Carbon held in roots, not spreadsheets" },
    { image: "", title: "Local crews", body: "Paid work for 34 people in the valley" },
]

interface Props {
    theme?: Theme
    brandFont?: boolean
    eyebrow?: string
    headline?: string
    highlight?: string
    body?: string
    emailPlaceholder?: string
    submitLabel?: string
    endpoint?: string
    socialProof?: string
    showAvatars?: boolean
    stats?: Stat[]
    image?: string
    imageAlt?: string
    imageFocus?: number
    cards?: FloatCard[]
    playLabel?: string
    playLink?: string
    style?: CSSProperties
}

/**
 * The Rootstock hero: copy and email capture on the left, artwork bleeding to
 * the panel's right edge with floating detail cards over it.
 *
 * Numbers in Stats count up when the section scrolls into view — write them as
 * plain numerals ("412,000+", "100%") and the digits animate.
 *
 * @framerSupportedLayoutWidth any
 * @framerSupportedLayoutHeight auto
 * @framerIntrinsicWidth 1440
 * @framerIntrinsicHeight 900
 */
export default function HeroSection(props: Props) {
    const {
        theme = "auto",
        brandFont = true,
        eyebrow = "Regenerative farm · Est. 2016",
        headline = "Grow food.\nGrow forests.",
        highlight = "forests",
        body = DEFAULT_BODY,
        emailPlaceholder = "Enter your email",
        submitLabel = "Join us",
        endpoint = "",
        socialProof = "Join 15,400+ people growing woodland",
        showAvatars = true,
        stats = DEFAULT_STATS,
        image = "",
        imageAlt = "Restored woodland meeting bare farmland",
        imageFocus = 46,
        cards = DEFAULT_CARDS,
        playLabel = "Watch our story",
        playLink = "",
        style,
    } = props
    const { ref, wrapper } = useSection(theme, brandFont)
    const capture = useEmailCapture(endpoint, "hero")

    return (
        <div {...wrapper} ref={ref} style={style}>
            <section className="hero">
                <div className="wrap">
                    <div className="hero-shell">
                        <div className="hero-copy">
                            {eyebrow ? (
                                <span className="eyebrow eyebrow-chip" data-reveal="fade">
                                    {eyebrow}
                                </span>
                            ) : null}

                            <h1 className="display" data-reveal>
                                {renderHighlight(headline, highlight)}
                            </h1>

                            {body ? (
                                <p className="lead" data-reveal style={{ ["--reveal-delay" as any]: "120ms" }}>
                                    {body}
                                </p>
                            ) : null}

                            <form className="stack" noValidate onSubmit={capture.submit} data-reveal
                                style={{ ["--reveal-delay" as any]: "200ms" }}>
                                <div className="inline-form">
                                    <label className="sr-only" htmlFor="rootstock-hero-email">Email address</label>
                                    <input
                                        className="input"
                                        id="rootstock-hero-email"
                                        type="email"
                                        name="email"
                                        placeholder={emailPlaceholder}
                                        value={capture.email}
                                        onChange={(e) => capture.setEmail(e.target.value)}
                                        aria-invalid={capture.state === "error"}
                                    />
                                    <button className={`btn btn-primary${capture.state === "busy" ? " is-loading" : ""}`} type="submit">
                                        <span>{submitLabel}</span> <ArrowIcon className="btn-ico" size={15} />
                                    </button>
                                </div>
                                {capture.message ? (
                                    <p className={`form-status is-shown${capture.state === "error" ? " is-error" : ""}`} role="status">
                                        {capture.message}
                                    </p>
                                ) : null}
                            </form>

                            {socialProof ? (
                                <div className="cluster gap-sm" data-reveal style={{ ["--reveal-delay" as any]: "280ms" }}>
                                    {showAvatars ? (
                                        <div className="avatars">
                                            <img src={assets.avatarA} alt="" width={40} height={40} />
                                            <img src={assets.avatarB} alt="" width={40} height={40} />
                                            <img src={assets.avatarC} alt="" width={40} height={40} />
                                        </div>
                                    ) : null}
                                    <p className="small muted">{socialProof}</p>
                                </div>
                            ) : null}

                            {stats.length ? (
                                <div className="hero-stats stagger" data-reveal="fade">
                                    {stats.map((stat, i) => (
                                        <div className={`stat${stat.tint ? " stat-hero" : ""}`} key={i}>
                                            <div className="stat-value">{renderNumber(stat.value)}</div>
                                            <div className="stat-label">{stat.label}</div>
                                        </div>
                                    ))}
                                </div>
                            ) : null}
                        </div>

                        <div className="hero-media">
                            {image ? (
                                <img src={image} alt={imageAlt} style={{ objectPosition: `${imageFocus}% 50%` }} />
                            ) : (
                                <div
                                    aria-hidden="true"
                                    style={{
                                        position: "absolute",
                                        inset: 0,
                                        background:
                                            "linear-gradient(100deg, var(--forest-800) 0%, var(--forest-500) 34%, var(--sand-300) 62%, var(--clay-300) 100%)",
                                    }}
                                />
                            )}

                            {cards.map((card, i) => (
                                <div className={`hero-float hero-float-${i + 1}`} key={i}>
                                    {card.image ? <img src={card.image} alt="" /> : null}
                                    <div>
                                        <strong>{card.title}</strong>
                                        <span>{card.body}</span>
                                    </div>
                                </div>
                            ))}

                            {playLabel ? (
                                <a className="hero-play" href={playLink || "#"}>
                                    <span className="play-btn rel">
                                        <svg className="ico" width={16} height={16} viewBox="0 0 24 24" fill="none"
                                            stroke="currentColor" strokeWidth={1.75} strokeLinejoin="round" aria-hidden="true">
                                            <path d="M8 5.5v13l11-6.5Z" />
                                        </svg>
                                    </span>
                                    <span>{playLabel}</span>
                                </a>
                            ) : null}
                        </div>
                    </div>
                </div>
            </section>
        </div>
    )
}

/* Wraps every occurrence of `highlight` in the brand green, and turns a
   newline in the headline into a line break. */
function renderHighlight(text: string, highlight: string) {
    const lines = (text || "").split("\n")
    return lines.map((line, li) => (
        <span key={li}>
            {highlight
                ? line.split(new RegExp(`(${escapeRegExp(highlight)})`, "gi")).map((part, i) =>
                      part.toLowerCase() === highlight.toLowerCase() ? (
                          <span className="hl" key={i}>{part}</span>
                      ) : (
                          <span key={i}>{part}</span>
                      )
                  )
                : line}
            {li < lines.length - 1 ? <br /> : null}
        </span>
    ))
}

/* "412,000+" animates the digits and keeps the suffix static. */
function renderNumber(value: string) {
    const m = /^([^\d]*)([\d.,]+)(.*)$/.exec(value || "")
    if (!m) return value
    const digits = m[2].replace(/,/g, "")
    const decimals = digits.includes(".") ? digits.split(".")[1].length : 0
    return (
        <>
            {m[1]}
            <span data-count={digits} data-decimals={decimals}>0</span>
            {m[3]}
        </>
    )
}

function escapeRegExp(s: string) {
    return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")
}

function ArrowIcon({ size = 16, className = "" }: { size?: number; className?: string }) {
    return (
        <svg className={`ico ${className}`} width={size} height={size} viewBox="0 0 24 24" fill="none"
            stroke="currentColor" strokeWidth={1.75} strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <path d="M5 12h14M13 6l6 6-6 6" />
        </svg>
    )
}


addPropertyControls(HeroSection, {
    theme: {
        type: ControlType.Enum, title: "Theme", options: ["auto", "light", "dark"],
        optionTitles: ["Auto", "Light", "Dark"], defaultValue: "auto",
    },
    eyebrow: { type: ControlType.String, title: "Eyebrow", defaultValue: "Regenerative farm · Est. 2016" },
    headline: {
        type: ControlType.String, title: "Headline", displayTextArea: true,
        defaultValue: "Grow food.\nGrow forests.",
    },
    highlight: {
        type: ControlType.String, title: "Highlight", defaultValue: "forests",
        description: "This word is shown in the brand green.",
    },
    body: { type: ControlType.String, title: "Body", displayTextArea: true, defaultValue: DEFAULT_BODY },
    image: { type: ControlType.Image, title: "Artwork" },
    imageAlt: { type: ControlType.String, title: "Alt text", defaultValue: "Restored woodland meeting bare farmland" },
    imageFocus: {
        type: ControlType.Number, title: "Focus", min: 0, max: 100, step: 1, unit: "%",
        defaultValue: 46, description: "Horizontal crop of the artwork.",
    },
    emailPlaceholder: { type: ControlType.String, title: "Placeholder", defaultValue: "Enter your email" },
    submitLabel: { type: ControlType.String, title: "Submit", defaultValue: "Join us" },
    endpoint: {
        type: ControlType.String, title: "Endpoint",
        description: "POST target for sign-ups. Left empty, the form confirms without sending.",
    },
    socialProof: { type: ControlType.String, title: "Proof", defaultValue: "Join 15,400+ people growing woodland" },
    showAvatars: { type: ControlType.Boolean, title: "Avatars", defaultValue: true },
    stats: {
        type: ControlType.Array, title: "Stats", maxCount: 4, defaultValue: DEFAULT_STATS,
        control: {
            type: ControlType.Object,
            controls: {
                value: { type: ControlType.String, title: "Value", defaultValue: "100%" },
                label: { type: ControlType.String, title: "Label", defaultValue: "Label" },
                tint: { type: ControlType.Boolean, title: "Tinted", defaultValue: false },
            },
        },
    },
    cards: {
        type: ControlType.Array, title: "Float cards", maxCount: 3, defaultValue: DEFAULT_CARDS,
        control: {
            type: ControlType.Object,
            controls: {
                image: { type: ControlType.Image, title: "Thumb" },
                title: { type: ControlType.String, title: "Title", defaultValue: "Title" },
                body: { type: ControlType.String, title: "Body", defaultValue: "One short line." },
            },
        },
    },
    playLabel: { type: ControlType.String, title: "Play label", defaultValue: "Watch our story" },
    playLink: { type: ControlType.Link, title: "Play link" },
    brandFont: {
        type: ControlType.Boolean, title: "Brand font", defaultValue: true,
        description: "Uses the bundled Plus Jakarta Sans. Turn off to inherit the Framer project's font.",
    },
})
