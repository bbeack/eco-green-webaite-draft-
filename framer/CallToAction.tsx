import { addPropertyControls, ControlType } from "framer"
import type { CSSProperties } from "react"
import { useSection, type Theme } from "./RootstockHooks"

const DEFAULT_BODY =
    "Fund a single tree, keep a grove growing every month, or bring your team to the hillside for a day that people actually talk about afterwards."

interface Props {
    theme?: Theme
    brandFont?: boolean
    badge?: string
    headline?: string
    body?: string
    primaryLabel?: string
    primaryLink?: string
    secondaryLabel?: string
    secondaryLink?: string
    onPaper?: boolean
    style?: CSSProperties
}

/**
 * The dark call-to-action panel. Leave "On paper" on to keep the warm page
 * margin around it, as on the site; turn it off to sit flush in a Framer stack.
 *
 * @framerSupportedLayoutWidth any
 * @framerSupportedLayoutHeight auto
 * @framerIntrinsicWidth 1440
 * @framerIntrinsicHeight 420
 */
export default function CallToAction(props: Props) {
    const {
        theme = "auto",
        brandFont = true,
        badge = "Planting season opens 1 November",
        headline = "Three pounds. One tree.\nA hundred years.",
        body = DEFAULT_BODY,
        primaryLabel = "Plant a tree",
        primaryLink = "",
        secondaryLabel = "Join a planting day",
        secondaryLink = "",
        onPaper = true,
        style,
    } = props
    const { ref, wrapper } = useSection(theme, brandFont)

    return (
        <div {...wrapper} ref={ref} style={style}>
            <section className={onPaper ? "section-plain" : undefined}
                style={onPaper ? undefined : { padding: 0 }}>
                <div className="cta-band" data-reveal="zoom">
                    {badge ? (
                        <span className="badge badge-accent">
                            <LeafIcon /> {badge}
                        </span>
                    ) : null}
                    <h2>
                        {headline.split("\n").map((line, i, all) => (
                            <span key={i}>
                                {line}
                                {i < all.length - 1 ? <br /> : null}
                            </span>
                        ))}
                    </h2>
                    {body ? <p>{body}</p> : null}
                    <div className="cluster">
                        {primaryLabel ? (
                            <a className="btn btn-accent btn-lg" href={primaryLink || "#"}>
                                {primaryLabel} <ArrowIcon />
                            </a>
                        ) : null}
                        {secondaryLabel ? (
                            <a className="btn btn-on-dark btn-lg" href={secondaryLink || "#"}>
                                {secondaryLabel}
                            </a>
                        ) : null}
                    </div>
                </div>
            </section>
        </div>
    )
}

function ArrowIcon() {
    return (
        <svg className="ico btn-ico" width={16} height={16} viewBox="0 0 24 24" fill="none" stroke="currentColor"
            strokeWidth={1.75} strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <path d="M5 12h14M13 6l6 6-6 6" />
        </svg>
    )
}
function LeafIcon() {
    return (
        <svg className="ico" width={14} height={14} viewBox="0 0 24 24" fill="none" stroke="currentColor"
            strokeWidth={1.75} strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z" />
            <path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12" />
        </svg>
    )
}


addPropertyControls(CallToAction, {
    theme: {
        type: ControlType.Enum, title: "Theme", options: ["auto", "light", "dark"],
        optionTitles: ["Auto", "Light", "Dark"], defaultValue: "auto",
    },
    badge: { type: ControlType.String, title: "Badge", defaultValue: "Planting season opens 1 November" },
    headline: {
        type: ControlType.String, title: "Headline", displayTextArea: true,
        defaultValue: "Three pounds. One tree.\nA hundred years.",
    },
    body: { type: ControlType.String, title: "Body", displayTextArea: true, defaultValue: DEFAULT_BODY },
    primaryLabel: { type: ControlType.String, title: "Primary", defaultValue: "Plant a tree" },
    primaryLink: { type: ControlType.Link, title: "Primary link" },
    secondaryLabel: { type: ControlType.String, title: "Secondary", defaultValue: "Join a planting day" },
    secondaryLink: { type: ControlType.Link, title: "Secondary link" },
    onPaper: {
        type: ControlType.Boolean, title: "On paper", defaultValue: true,
        description: "Keeps the warm page margin around the panel.",
    },
    brandFont: {
        type: ControlType.Boolean, title: "Brand font", defaultValue: true,
        description: "Uses the bundled Plus Jakarta Sans. Turn off to inherit the Framer project's font.",
    },
})
