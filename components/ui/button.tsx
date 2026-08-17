import { ButtonHTMLAttributes } from "react";

// Kept locally, in the shadcn/ui ownership model, so it can be evolved with the product.
export function Button({ className = "", ...props }: ButtonHTMLAttributes<HTMLButtonElement>) {
  return <button className={`primary ${className}`} {...props} />;
}
