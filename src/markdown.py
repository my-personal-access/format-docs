"""Manage markdown."""
import src.constants as cst

def altair_to_urssaf(md: str) -> str:
    """Change old FQDN to new FQDN."""
    old = "redmine.altair.recouv"
    new = "redmine.urssaf.recouv"
    
    md__ = md.replace(old, new)
    
    if md != md__:
        cst.review_log.info(f"{old} ---> {new}")
    return md__