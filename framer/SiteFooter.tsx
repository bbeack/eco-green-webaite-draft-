import { addPropertyControls, ControlType } from "framer"
import type { CSSProperties } from "react"
import { useRootstock, useEmailCapture, assets, type Theme } from "./RootstockHooks"

interface FooterLink {
    label: string
    link: string
}
interface Column {
    heading: string
    links: FooterLink[]
}
const DEFAULT_BLURB =
    "Together, we can grow a valley that feeds people and forests for generations to come."
const DEFAULT_ADDRESS = "Cwm Aeron Farm, Hay-on-Wye, Powys HR3 5QA\nFarm shop open Fri–Sun, 9–4"
const DEFAULT_LEGAL =
    "© 2026 Rootstock Farm & Forest CIC. Company no. 11902847. A not-for-profit community interest company."

const DEFAULT_COLUMNS: Column[] = [
    {
        heading: "Explore",
        links: [
            { label: "Home", link: "" }, { label: "Our Farm", link: "" },
            { label: "Forest Projects", link: "" }, { label: "Get Involved", link: "" },
            { label: "Contact", link: "" },
        ],
    },
    {
        heading: "Get Involved",
        links: [
            { label: "Plant a tree", link: "" }, { label: "Become a Grove Keeper", link: "" },
            { label: "Volunteer days", link: "" }, { label: "Partner with us", link: "" },
        ],
    },
    {
        heading: "Support",
        links: [
            { label: "FAQs", link: "" }, { label: "Impact reporting", link: "" },
            { label: "Privacy policy", link: "" }, { label: "Terms of use", link: "" },
            { label: "Accessibility", link: "" },
        ],
    },
]

const DEFAULT_SOCIAL: FooterLink[] = [
    { label: "X", link: "" }, { label: "Instagram", link: "" },
    { label: "Facebook", link: "" }, { label: "LinkedIn", link: "" },
]

interface Props {
    theme?: Theme
    brandFont?: boolean
    logo?: string
    brandName?: string
    brandKicker?: string
    blurb?: string
    showSignup?: boolean
    emailPlaceholder?: string
    endpoint?: string
    columns?: Column[]
    socialHeading?: string
    social?: FooterLink[]
    visitHeading?: string
    address?: string
    email?: string
    legal?: string
    note?: string
    style?: CSSProperties
}

/**
 * Rootstock site footer: brand and sign-up, link columns, socials and the
 * legal line.
 *
 * @framerSupportedLayoutWidth any
 * @framerSupportedLayoutHeight auto
 * @framerIntrinsicWidth 1440
 * @framerIntrinsicHeight 480
 */
export default function SiteFooter(props: Props) {
    const {
        theme = "auto",
        brandFont = true,
        logo = "",
        brandName = "Rootstock",
        brandKicker = "Farm & Forest",
        blurb = DEFAULT_BLURB,
        showSignup = true,
        emailPlaceholder = "Enter your email",
        endpoint = "",
        columns = DEFAULT_COLUMNS,
        socialHeading = "Follow Us",
        social = DEFAULT_SOCIAL,
        visitHeading = "Visit",
        address = DEFAULT_ADDRESS,
        email = "hello@rootstock.earth",
        legal = DEFAULT_LEGAL,
        note = "100% of trading profit funds planting",
        style,
    } = props
    const wrapper = useRootstock(theme, brandFont)
    const capture = useEmailCapture(endpoint, "footer")

    return (
        <div {...wrapper} style={style}>
            <footer className="footer">
                <div className="footer-grid">
                    <div>
                        <a className="brand" href="#">
                            <img src={logo || assets.logo} alt="" width={32} height={32} />
                            <span className="brand-name">
                                {brandName}
                                {brandKicker ? <small>{brandKicker}</small> : null}
                            </span>
                        </a>
                        {blurb ? <p className="small mt-4" style={{ maxWidth: "28ch" }}>{blurb}</p> : null}

                        {showSignup ? (
                            <form className="mt-5" noValidate onSubmit={capture.submit}>
                                <div className="inline-form">
                                    <label className="sr-only" htmlFor="rootstock-footer-email">Email address</label>
                                    <input
                                        className="input"
                                        id="rootstock-footer-email"
                                        type="email"
                                        placeholder={emailPlaceholder}
                                        value={capture.email}
                                        onChange={(e) => capture.setEmail(e.target.value)}
                                        aria-invalid={capture.state === "error"}
                                    />
                                    <button className="btn btn-primary btn-sm" type="submit" aria-label="Subscribe">
                                        <svg className="ico" width={15} height={15} viewBox="0 0 24 24" fill="none"
                                            stroke="currentColor" strokeWidth={1.75} strokeLinecap="round"
                                            strokeLinejoin="round" aria-hidden="true">
                                            <path d="M5 12h14M13 6l6 6-6 6" />
                                        </svg>
                                    </button>
                                </div>
                                {capture.message ? (
                                    <p className={`form-status is-shown${capture.state === "error" ? " is-error" : ""}`}
                                        role="status" style={{ marginTop: "0.75rem" }}>
                                        {capture.message}
                                    </p>
                                ) : null}
                            </form>
                        ) : null}
                    </div>

                    {columns.map((col, i) => (
                        <div key={i}>
                            <h4>{col.heading}</h4>
                            <div className="footer-links">
                                {col.links.map((l, j) => (
                                    <a key={j} href={l.link || "#"}>{l.label}</a>
                                ))}
                            </div>
                        </div>
                    ))}

                    <div>
                        {socialHeading ? <h4>{socialHeading}</h4> : null}
                        <div className="social">
                            {social.map((s, i) => (
                                <a key={i} href={s.link || "#"} target="_blank" rel="noopener"
                                    aria-label={`${brandName} on ${s.label} (opens in a new tab)`}>
                                    <SocialIcon name={s.label} />
                                </a>
                            ))}
                        </div>
                        {visitHeading ? <h4 className="mt-6">{visitHeading}</h4> : null}
                        {address ? (
                            <p className="small">
                                {address.split("\n").map((line, i, all) => (
                                    <span key={i}>{line}{i < all.length - 1 ? <br /> : null}</span>
                                ))}
                            </p>
                        ) : null}
                        {email ? (
                            <p className="small mt-3"><a href={`mailto:${email}`}>{email}</a></p>
                        ) : null}
                    </div>
                </div>

                <div className="footer-bottom">
                    <p>{legal}</p>
                    {note ? <p className="cluster gap-sm">{note}</p> : null}
                </div>
            </footer>
        </div>
    )
}

const SOCIAL_PATHS: Record<string, string> = {
    x: "M22 5.9a8 8 0 0 1-2.4.7 4 4 0 0 0 1.8-2.2 8.2 8.2 0 0 1-2.6 1A4.1 4.1 0 0 0 11.8 9 11.6 11.6 0 0 1 3.4 4.7a4.1 4.1 0 0 0 1.3 5.5 4 4 0 0 1-1.9-.5 4.1 4.1 0 0 0 3.3 4 4.1 4.1 0 0 1-1.9.1 4.1 4.1 0 0 0 3.8 2.9A8.3 8.3 0 0 1 2 18.4a11.6 11.6 0 0 0 6.3 1.8c7.5 0 11.7-6.3 11.5-12a8.2 8.2 0 0 0 2.2-2.3Z",
    instagram: "M8 3h8a5 5 0 0 1 5 5v8a5 5 0 0 1-5 5H8a5 5 0 0 1-5-5V8a5 5 0 0 1 5-5Zm4 5a4 4 0 1 0 0 8 4 4 0 0 0 0-8Z",
    facebook: "M14 8.5V7c0-1 .4-1.5 1.6-1.5H17V2.5h-2.4C11.8 2.5 11 4 11 6.4v2.1H9V12h2v9.5h3V12h2.3l.4-3.5Z",
    linkedin: "M4 3h16a1 1 0 0 1 1 1v16a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1Zm4 7v7m0-10v.01M12 17v-3.8c0-1.2.8-2.2 2-2.2s2 1 2 2.2V17",
    youtube: "M2.5 9a4 4 0 0 1 4-4h11a4 4 0 0 1 4 4v6a4 4 0 0 1-4 4h-11a4 4 0 0 1-4-4Zm8 0 5 3-5 3Z",
}

function SocialIcon({ name }: { name: string }) {
    const key = (name || "").toLowerCase().replace(/[^a-z]/g, "")
    const d = SOCIAL_PATHS[key] || SOCIAL_PATHS.x
    return (
        <svg className="ico" width={16} height={16} viewBox="0 0 24 24" fill="none" stroke="currentColor"
            strokeWidth={1.6} strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <path d={d} />
        </svg>
    )
}


addPropertyControls(SiteFooter, {
    theme: {
        type: ControlType.Enum, title: "Theme", options: ["auto", "light", "dark"],
        optionTitles: ["Auto", "Light", "Dark"], defaultValue: "auto",
    },
    logo: { type: ControlType.Image, title: "Logo" },
    brandName: { type: ControlType.String, title: "Brand", defaultValue: "Rootstock" },
    brandKicker: { type: ControlType.String, title: "Kicker", defaultValue: "Farm & Forest" },
    blurb: { type: ControlType.String, title: "Blurb", displayTextArea: true, defaultValue: DEFAULT_BLURB },
    showSignup: { type: ControlType.Boolean, title: "Sign-up", defaultValue: true },
    emailPlaceholder: { type: ControlType.String, title: "Placeholder", defaultValue: "Enter your email" },
    endpoint: { type: ControlType.String, title: "Endpoint" },
    columns: {
        type: ControlType.Array, title: "Columns", maxCount: 3, defaultValue: DEFAULT_COLUMNS,
        control: {
            type: ControlType.Object,
            controls: {
                heading: { type: ControlType.String, title: "Heading", defaultValue: "Column" },
                links: {
                    type: ControlType.Array, title: "Links",
                    control: {
                        type: ControlType.Object,
                        controls: {
                            label: { type: ControlType.String, title: "Label", defaultValue: "Link" },
                            link: { type: ControlType.Link, title: "Link" },
                        },
                    },
                },
            },
        },
    },
    socialHeading: { type: ControlType.String, title: "Social heading", defaultValue: "Follow Us" },
    social: {
        type: ControlType.Array, title: "Social", defaultValue: DEFAULT_SOCIAL,
        control: {
            type: ControlType.Object,
            controls: {
                label: {
                    type: ControlType.Enum, title: "Network",
                    options: ["X", "Instagram", "Facebook", "LinkedIn", "YouTube"],
                    defaultValue: "X",
                },
                link: { type: ControlType.Link, title: "Link" },
            },
        },
    },
    visitHeading: { type: ControlType.String, title: "Visit heading", defaultValue: "Visit" },
    address: { type: ControlType.String, title: "Address", displayTextArea: true, defaultValue: DEFAULT_ADDRESS },
    email: { type: ControlType.String, title: "Email", defaultValue: "hello@rootstock.earth" },
    legal: { type: ControlType.String, title: "Legal", displayTextArea: true, defaultValue: DEFAULT_LEGAL },
    note: { type: ControlType.String, title: "Note", defaultValue: "100% of trading profit funds planting" },
    brandFont: {
        type: ControlType.Boolean, title: "Brand font", defaultValue: true,
        description: "Uses the bundled Plus Jakarta Sans. Turn off to inherit the Framer project's font.",
    },
})
