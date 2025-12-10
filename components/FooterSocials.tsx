import Link from 'next/link';
import Image from 'next/image';

const SOCIAL_LINKS = [
  {
    label: 'Instagram',
    href: 'https://www.instagram.com/kashrock.py?igsh=MXNpcW9idDR3dXBjZA%3D%3D&utm_source=qr',
    icon: '/icons/instagram.svg',
  },
  {
    label: 'Twitter',
    href: 'https://x.com/kashrockpy?s=21',
    icon: '/icons/twitter.svg',
  },
  {
    label: 'RapidAPI',
    href: 'https://rapidapi.com/user/kashrock',
    icon: '/icons/rapidapi.svg',
  },
  {
    label: 'Discord',
    href: 'https://discord.gg/c8tknxpMg8',
    icon: '/icons/discord.svg',
  },
];

interface FooterSocialsProps {
  size?: 'sm' | 'md';
  className?: string;
}

const classNames = (...values: Array<string | undefined>) => values.filter(Boolean).join(' ');

export default function FooterSocials({ size = 'md', className }: FooterSocialsProps) {
  const dimension = size === 'sm' ? 36 : 48;

  return (
    <div className={classNames('flex flex-wrap items-center gap-3 sm:gap-4', className)}>
      {SOCIAL_LINKS.map((social) => (
        <Link
          key={social.label}
          href={social.href}
          target="_blank"
          rel="noopener noreferrer"
          className="group focus:outline-none focus-visible:ring-2 focus-visible:ring-[#7C3AED] rounded-full"
          aria-label={social.label}
        >
          <div className="rounded-full bg-white border border-[#E5E1EF] shadow-sm shadow-[#0000000f] transition-all duration-200 hover:-translate-y-0.5 hover:shadow-lg hover:border-[#C5BDD5] p-2">
            <Image
              src={social.icon}
              alt={social.label}
              width={dimension}
              height={dimension}
              className="w-9 h-9 object-contain"
            />
          </div>
        </Link>
      ))}
    </div>
  );
}
