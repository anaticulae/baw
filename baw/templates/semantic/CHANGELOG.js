# CHANGELOG

Every noteable change is logged here.

{%    for version, release in ctx.history.released.items()
%}{{
        "## %s (%s)" | format(version.as_tag(), release.tagged_date.strftime("%Y-%m-%d"))

}}{%    for type_, commits in release["elements"] if type_ != "unknown" | dictsort
%}{{
          "### %s" | format(type_ | title)

}}{%      for commit in commits
%}{{
            "* %s ([`%s`](%s))" | format(
              commit.descriptions[0] | capitalize,
              commit.hexsha[:7],
              commit.hexsha | commit_hash_url,
            )

}}{%      endfor
%}{%    endfor
%}{%  endfor
%}
