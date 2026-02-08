import { Router } from "express";
import { explainCode } from "./explainCode.controller.js";


const router = Router();

router.route("/").post(explainCode)

export default router