package com.ctf.shiro.controller;

import org.apache.shiro.SecurityUtils;
import org.apache.shiro.authc.UsernamePasswordToken;
import org.apache.shiro.subject.Subject;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

@Controller
public class HomeController {

    @Value("${leaderboard.url:http://localhost:80}")
    private String leaderboardUrl;

    @GetMapping("/")
    public String index(Model model) {
        Subject subject = SecurityUtils.getSubject();
        model.addAttribute("username", subject.getPrincipal());
        model.addAttribute("leaderboardUrl", leaderboardUrl);
        return "index";
    }

    @GetMapping("/login")
    public String loginPage(Model model,
                            @RequestParam(required = false) String error) {
        if (error != null) {
            model.addAttribute("error", "Invalid username or password");
        }
        return "login";
    }

    @PostMapping("/login")
    public String login(@RequestParam String username,
                        @RequestParam String password,
                        @RequestParam(defaultValue = "false") boolean rememberMe) {
        Subject subject = SecurityUtils.getSubject();
        UsernamePasswordToken token = new UsernamePasswordToken(username, password, rememberMe);
        try {
            subject.login(token);
            return "redirect:/";
        } catch (Exception e) {
            return "redirect:/login?error=1";
        }
    }

    @GetMapping("/logout")
    public String logout() {
        SecurityUtils.getSubject().logout();
        return "redirect:/login";
    }
}
